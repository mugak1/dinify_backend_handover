def make_menu_group_messages(msg_data, footer) -> dict:
    message = {
        'email': None,
        'sms': None,
        'subject': None
    }

    if msg_data.get('msg_type') == 'new-menu-group':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has added a new menu group, {msg_data['item_name']}.&nbsp;</span></p>
        <p><span style="font-weight:400;">You can now add items to the group and customers will be able to order for respective accordingly.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Group Created',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-updated':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has updated the details for the menu group, {msg_data['item_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Group Updated',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-disabled':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has disabled the menu group, {msg_data['item_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Group Disabled',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-enabled':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has enabled the menu group, {msg_data['item_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Group Enabled',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-group-deleted':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p><br><span style="font-weight:400;">{msg_data['user']} has deleted the menu group, {msg_data['item_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Group Deleted',
            'email': email,
            'sms': None
        }

    return message
