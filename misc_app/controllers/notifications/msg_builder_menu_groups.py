def make_menu_group_messages(msg_data, footer) -> dict:
    message = {
        'email': None,
        'sms': None,
        'subject': None
    }

    if msg_data.get('msg_type') == 'new-menu-group':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has added a new menu group, {msg_data['group_name']}.&nbsp;</span></p>
        <br><p></p>
        <p><span style="font-weight: 400;">
        You can now add items to the group and customers will be able to order for the items accordingly.&nbsp;</span></p>
        </span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-updated':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has updated the details for the menu group, {msg_data['group_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-disabled':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has disabled the menu group, {msg_data['group_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-enabled':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has enabled the menu group, {msg_data['group_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-deleted':
        email = f"""
        <p><span style="font-weight: 400;">Hello {msg_data['restaurant_name']},</span></p>
        <br><p></p>

        <p><span style="font-weight: 400;">
        {msg_data['user']} has deleted the menu group, {msg_data['group_name']}.&nbsp;</span></p>
        <br><p></p>
        {footer}
        """
        message = {
            'email': email,
            'sms': None
        }

    return message
