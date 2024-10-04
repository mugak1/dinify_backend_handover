def make_menu_messages(msg_data, footer) -> dict:
    message = {
        'email': None,
        'sms': None,
        'subject': None
    }
    if msg_data.get('msg_type') == 'first-time-batch-approval':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">The menu has been approved.&nbsp;</span></p>
        <p><span style="font-weight:400;">Customers can now see the items on your menu and place orders accordingly.&nbsp;</span></p>{footer}
        """
        message = {
            'subject': 'Restaurant First Time Menu Approval',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'new-menu-section':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has added a new menu section, {msg_data['section_name']}.&nbsp;</span></p>
        <p><span style="font-weight:400;">You can now add items to the section and customers will be able to order for the items accordingly.&nbsp;</span></p>{footer}
        """
        message = {
            'subject': 'New Menu Section',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-section-updated':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has updated the details for the menu section, {msg_data['section_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Section Updated',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-section-disabled':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has disabled the menu section, {msg_data['section_name']}.&nbsp;</span></p>        
        {footer}
        """
        message = {
            'subject': 'Menu Section Disabled',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-section-enabled':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has enabled the menu section, {msg_data['section_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Section Enabled',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'menu-section-deleted':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['restaurant_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">{msg_data['user']} has deleted the menu section, {msg_data['section_name']}.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Menu Section Deleted',
            'email': email,
            'sms': None
        }

    return message
