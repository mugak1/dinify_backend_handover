def make_restaurant_messages(msg_data, footer) -> dict:
    message = {
        'email': None,
        'sms': None,
        'subject': None
    }

    if msg_data.get('msg_type') == 'new-restaurant':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['first_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">Your application for the restaurant, {msg_data['restaurant_name']}, has been submitted to Dinify.&nbsp;</span></p>
        <p><span style="font-weight:400;">We shall review the details and get back to you as soon as possible.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'Restaurant Profile Submitted to Dinify',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'admin-new-restaurant':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['first_name']},</span></p>
        <p><br><span style="font-weight:400;">A profile for your restaurant, {msg_data['restaurant_name']}, has been created on Dinify.&nbsp;</span></p>
        <p><span style="font-weight:400;">We shall confirm the details and get back to you as soon as possible.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'New Restaurant Created on Dinify',
            'email': email,
            'sms': None
        }

    elif msg_data.get('msg_type') == 'new-restaurant-employee':
        email = f"""
        <p><span style="font-weight:400;">Hello {msg_data['first_name']},</span></p>
        <p>&nbsp;</p>
        <p><span style="font-weight:400;">You have been granted access to the restaurant, {msg_data['restaurant_name']} on Dinify.&nbsp;</span></p>
        <p><span style="font-weight:400;">You can now access the restaurant's account and perform your respective duties.&nbsp;</span></p>
        {footer}
        """
        message = {
            'subject': 'User Profile Added to Restaurant',
            'email': email,
            'sms': None
        }

    return message
