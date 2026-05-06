"""
Temporary read-only verification command for the discount math fix.

Confirms migration 0042 (canonical discount_details shape) and the frontend
canonical-write fix landed correctly on UAT. To be removed in a follow-up PR
after the fix is confirmed clean.

Performs four passes; every pass is read-only (no .save(), no .create(),
no .delete()).
"""
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand

from restaurants_app.models import MenuItem


BUGGY_KEYS = ('raw_discount_value', 'raw_discount_type')
TOLERANCE = Decimal('0.01')


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')


def _quantize_money(value):
    if value < 0:
        return Decimal('0.00')
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _restaurant_id(item):
    try:
        return str(item.section.restaurant_id)
    except Exception:
        return '<unknown>'


class Command(BaseCommand):
    help = (
        'Verify the discount math fix (migration 0042 + frontend canonical '
        'writes) landed correctly. Read-only.'
    )

    def handle(self, *args, **options):
        failures = []

        p1_total, p1_buggy = self._pass_1_migration_completeness()
        if p1_buggy != 0:
            failures.append(1)

        p2_nonempty, p2_conforming = self._pass_2_canonical_shape()
        if p2_conforming != p2_nonempty:
            failures.append(2)

        p3_total, p3_matching = self._pass_3_discounted_price_consistency()
        if p3_matching != p3_total:
            failures.append(3)

        p4_total, p4_correct = self._pass_4_order_pricing_simulation()
        if p4_correct != p4_total:
            failures.append(4)

        self.stdout.write('')
        self.stdout.write('=== SUMMARY ===')
        self._summary_line(1, 'Migration completeness',
                           f'{p1_total} items checked, {p1_buggy} buggy',
                           p1_buggy == 0)
        self._summary_line(2, 'Canonical shape conformance',
                           f'{p2_conforming}/{p2_nonempty} conforming',
                           p2_conforming == p2_nonempty)
        self._summary_line(3, 'discounted_price consistency',
                           f'{p3_matching}/{p3_total} matching',
                           p3_matching == p3_total)
        self._summary_line(4, 'Order-pricing simulation',
                           f'{p4_correct}/{p4_total} correct',
                           p4_correct == p4_total)

        if failures:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(
                f'FAILED passes: {failures}'
            ))
            raise SystemExit(1)

    def _summary_line(self, num, label, detail, ok):
        marker = '✅' if ok else '❌'
        self.stdout.write(f'{marker} PASS {num}: {label} — {detail}')

    # ------------------------------------------------------------------
    # PASS 1
    # ------------------------------------------------------------------
    def _pass_1_migration_completeness(self):
        self.stdout.write('=== PASS 1: Migration completeness ===')
        total = 0
        buggy_items = []

        for item in MenuItem.objects.iterator(chunk_size=500):
            total += 1
            details = item.discount_details or {}
            if not isinstance(details, dict):
                continue
            if any(k in details for k in BUGGY_KEYS):
                buggy_items.append(item)

        self.stdout.write(f'Total MenuItems: {total}')
        self.stdout.write(
            f'Items with raw_* keys present: {len(buggy_items)} '
            f'(expected 0 post-migration)'
        )

        for item in buggy_items:
            self.stdout.write(
                f'  - id={item.id} name={item.name!r} '
                f'restaurant_id={_restaurant_id(item)} '
                f'discount_details={item.discount_details}'
            )

        if not buggy_items:
            self.stdout.write(self.style.SUCCESS('PASS 1 OK'))
        else:
            self.stdout.write(self.style.ERROR('PASS 1 FAILED'))
        self.stdout.write('')
        return total, len(buggy_items)

    # ------------------------------------------------------------------
    # PASS 2
    # ------------------------------------------------------------------
    def _pass_2_canonical_shape(self):
        self.stdout.write('=== PASS 2: Canonical shape conformance ===')
        nonempty = 0
        conforming = 0
        non_conforming = []

        for item in MenuItem.objects.iterator(chunk_size=500):
            details = item.discount_details or {}
            if not isinstance(details, dict) or not details:
                continue
            nonempty += 1

            failure_reason = self._check_canonical_shape(details)
            if failure_reason is None:
                conforming += 1
            else:
                non_conforming.append((item, failure_reason))

        self.stdout.write(f'Items with non-empty discount_details: {nonempty}')
        self.stdout.write(f'Conforming: {conforming}')
        self.stdout.write(f'Non-conforming: {len(non_conforming)}')

        for item, reason in non_conforming:
            self.stdout.write(
                f'  - id={item.id} name={item.name!r} '
                f'discount_details={item.discount_details} '
                f'failed_rule={reason!r}'
            )

        if conforming == nonempty:
            self.stdout.write(self.style.SUCCESS('PASS 2 OK'))
        else:
            self.stdout.write(self.style.ERROR('PASS 2 FAILED'))
        self.stdout.write('')
        return nonempty, conforming

    @staticmethod
    def _check_canonical_shape(details):
        dtype = details.get('discount_type')
        if dtype not in ('percentage', 'fixed'):
            return "discount_type must be 'percentage' or 'fixed'"
        if 'discount_percentage' not in details:
            return 'discount_percentage field missing'
        if 'discount_amount' not in details:
            return 'discount_amount field missing'

        pct = _to_decimal(details.get('discount_percentage', 0))
        amt = _to_decimal(details.get('discount_amount', 0))

        if dtype == 'percentage':
            if pct <= 0:
                return 'percentage type requires discount_percentage > 0'
            if amt != 0:
                return 'percentage type requires discount_amount == 0'
        else:  # fixed
            if amt <= 0:
                return 'fixed type requires discount_amount > 0'
            if pct != 0:
                return 'fixed type requires discount_percentage == 0'
        return None

    # ------------------------------------------------------------------
    # PASS 3
    # ------------------------------------------------------------------
    def _pass_3_discounted_price_consistency(self):
        self.stdout.write('=== PASS 3: discounted_price column consistency ===')
        total = 0
        matching = 0
        mismatches = []

        for item in MenuItem.objects.iterator(chunk_size=500):
            details = item.discount_details or {}
            if not isinstance(details, dict) or not details:
                continue
            total += 1

            recomputed = self._recompute_discounted_price(
                item.primary_price, details
            )
            stored = item.discounted_price
            if stored is None:
                mismatches.append((item, recomputed, stored))
                continue

            if abs(_to_decimal(stored) - recomputed) <= TOLERANCE:
                matching += 1
            else:
                mismatches.append((item, recomputed, stored))

        self.stdout.write(f'Items checked: {total}')
        self.stdout.write(f'Matching (within {TOLERANCE}): {matching}')
        self.stdout.write(f'Mismatched: {len(mismatches)}')

        for item, recomputed, stored in mismatches:
            self.stdout.write(
                f'  - id={item.id} name={item.name!r} '
                f'primary_price={item.primary_price} '
                f'discount_details={item.discount_details} '
                f'stored_discounted_price={stored} '
                f'recomputed={recomputed}'
            )

        if matching == total:
            self.stdout.write(self.style.SUCCESS('PASS 3 OK'))
        else:
            self.stdout.write(self.style.ERROR('PASS 3 FAILED'))
        self.stdout.write('')
        return total, matching

    @staticmethod
    def _recompute_discounted_price(primary_price, details):
        primary = _to_decimal(primary_price or 0)
        dtype = details.get('discount_type')
        pct = _to_decimal(details.get('discount_percentage', 0))
        amt = _to_decimal(details.get('discount_amount', 0))

        if dtype == 'percentage':
            return _quantize_money(
                primary * (Decimal('1') - pct / Decimal('100'))
            )
        if dtype == 'fixed':
            return _quantize_money(primary - amt)
        return _quantize_money(primary)

    # ------------------------------------------------------------------
    # PASS 4
    # ------------------------------------------------------------------
    def _pass_4_order_pricing_simulation(self):
        self.stdout.write('=== PASS 4: Order-pricing simulation ===')
        from orders_app.controllers.con_orders import ConOrder

        sample = list(
            MenuItem.objects.filter(running_discount=True)
            .exclude(discount_details={})
            .order_by('time_created')[:5]
        )
        if len(sample) < 5:
            extra = (
                MenuItem.objects.filter(consider_discount_object=True)
                .exclude(discount_details={})
                .exclude(pk__in=[i.pk for i in sample])
                .order_by('time_created')[: 5 - len(sample)]
            )
            sample.extend(list(extra))

        total = len(sample)
        correct = 0

        if total == 0:
            self.stdout.write(
                'No MenuItems with active discounts found to sample.'
            )
            self.stdout.write(self.style.SUCCESS('PASS 4 OK (vacuous)'))
            self.stdout.write('')
            return 0, 0

        for item in sample:
            details = item.discount_details or {}
            recomputed = self._recompute_discounted_price(
                item.primary_price, details
            )
            stored = item.discounted_price
            stored_dec = (
                _to_decimal(stored) if stored is not None else None
            )

            result = ConOrder.determine_effective_unit_price(menu_item=item)
            effective = result.get('price') if isinstance(result, dict) else None

            agree = (
                stored_dec is not None
                and effective is not None
                and abs(stored_dec - recomputed) <= TOLERANCE
                and abs(effective - recomputed) <= TOLERANCE
            )
            if agree:
                correct += 1

            self.stdout.write(
                f'  - id={item.id} name={item.name!r}\n'
                f'      primary_price={item.primary_price}\n'
                f'      discount_details={details}\n'
                f'      stored discounted_price={stored}\n'
                f'      recomputed canonical price={recomputed}\n'
                f'      effective_unit_price (ConOrder)={effective}\n'
                f'      agree={agree}'
            )

        self.stdout.write(
            'Sanity reference: a UGX 10,000 item with 20% discount must '
            "yield effective_unit_price=Decimal('8000.00'), "
            "NOT Decimal('2000.00')."
        )

        if correct == total:
            self.stdout.write(self.style.SUCCESS('PASS 4 OK'))
        else:
            self.stdout.write(self.style.ERROR('PASS 4 FAILED'))
        self.stdout.write('')
        return total, correct
