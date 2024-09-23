def make_menu_item_messages(msg_data, footer) -> dict:
    message = {
        'email': None,
        'sms': None,
        'subject': None
    }

    if msg_data.get('msg_type') == 'new-menu-item':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has added a new menu item, {msg_data['item_name']}.&nbsp;</span></p>
        <br><p></p>
        <p><span style="font-weight: 400;">
        Customers will now be able to order for the item.&nbsp;</span></p>
        </span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-item-updated':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has updated the details for the menu item, {msg_data['item_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-item-disabled':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has disabled the menu item, {msg_data['item_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-item-enabled':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has enabled the menu item, {msg_data['item_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-item-deleted':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has deleted the menu item, {msg_data['item_name']}.&nbsp;</span></p>
        <p><span style="font-weight: 400;">
        Reason for deleting: {msg_data['reason']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    return message
