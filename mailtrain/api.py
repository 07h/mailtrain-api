import re
import requests


class ApiError(Exception):
    """Error class for API errors"""

    pass


def validate_email(func):
    """Validate email address"""

    def wrapper(self, *args, **kwargs):
        email = kwargs.get("email", args[0])
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            raise ValueError("Invalid email address")
        return func(self, *args, **kwargs)

    return wrapper


def check_response(func):
    """Check response for errors"""

    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.json().get("error"):
            raise ApiError(response.json()["error"])
        response.raise_for_status()
        return response.json()["data"]

    return wrapper


class Mailtrain:
    def __init__(self, api_token: str, api_url: str):
        """Mailtrain API class
        :param api_token: The API token
        :param api_url: The API url like https://mailtrain.example.com or https://example.com
        """
        self.api_token = api_token
        self.api_url = api_url[:-1] if api_url.endswith("/") else api_url

    @check_response
    def get_subscribers(self, list_id: str, start: int = 0, limit: int = 10000) -> dict:
        """Get subscribers from a list

        :param list_id: The list id
        :param start: The start index
        :param limit: The limit of subscribers to get
        :return: A dict of subscribers
        """
        url = (
            self.api_url
            + "/api/subscriptions/"
            + list_id
            + "?access_token="
            + self.api_token
            + "&start="
            + str(start)
            + "&limit="
            + str(limit)
        )
        return requests.get(url)

    @validate_email
    @check_response
    def add_subscription(
        self,
        email: str,
        list_id: str,
        first_name: str = "",
        last_name: str = "",
        timezone: str = "",
        force_subscribe: bool = True,
        require_confirmation: bool = False,
        **kwargs
    ) -> dict:
        """Add or update a subscriber to a list

        :param email: The email address
        :param list_id: The list id
        :param first_name: The first name
        :param last_name: The last name
        :param timezone: subscriber's timezone (eg. "Europe/Tallinn", "PST" or "UTC"). If not set defaults to "UTC"
        :param force_subscribe: Force subscribe
        :param require_confirmation: Require confirmation
        :param kwargs: custom fields values like MERGE_*. Use yes/no for option group values (checkboxes, radios, drop downs)
        :return: A dict of the subscriber
        """
        url = (
            self.api_url
            + "/api/subscribe/"
            + list_id
            + "?access_token="
            + self.api_token
        )
        data = {
            "EMAIL": email,
            **kwargs,
        }
        if first_name:
            data["MERGE_FIRST_NAME"] = first_name
        if last_name:
            data["MERGE_LAST_NAME"] = last_name
        if timezone:
            data["TIMEZONE"] = timezone
        if force_subscribe:
            data["FORCE_SUBSCRIBE"] = "yes"
        if require_confirmation:
            data["REQUIRE_CONFIRMATION"] = "yes"
        return requests.post(url, data=data)

    # Alias for add_subscription
    update_subscription = add_subscription

    @validate_email
    @check_response
    def unsubscribe(self, email: str, list_id: str) -> dict:
        """Unsubscribe a subscriber from a list

        :param email: The email address
        :param list_id: The list id
        :return: A dict of the subscriber
        """
        url = (
            self.api_url
            + "/api/unsubscribe/"
            + list_id
            + "?access_token="
            + self.api_token
        )
        data = {"EMAIL": email}
        return requests.post(url, data=data)

    @validate_email
    def unsubscribe_from_all_lists(self, email: str) -> None:
        """Unsubscribe a subscriber from all lists

        :param email: The email address
        """
        for list_id in self.get_lists(email):
            self.unsubscribe(email, list_id["cid"])

        return True

    @validate_email
    @check_response
    def delete_subscription(self, email: str, list_id: str) -> dict:
        """Delete a subscriber from a list

        :param email: The email address
        :param list_id: The list id
        :return: A dict of the subscriber
        """
        url = (
            self.api_url + "/api/delete/" + list_id + "?access_token=" + self.api_token
        )
        data = {"EMAIL": email}
        return requests.post(url, data=data)

    @validate_email
    def delete_from_all_lists(self, email: str) -> None:
        """Delete a subscriber from all lists

        :param email: The email address
        """
        for list_id in self.get_lists(email):
            self.delete_subscription(email, list_id["cid"])

        return True

    @check_response
    def create_custom_field(
        self,
        list_id: str,
        name: str,
        type: str,
        group_template: str = "",
        group: str = "",
        visible: bool = True,
    ) -> dict:
        """Create a custom field for a list

        :param list_id: The list id
        :param name: The name of the custom field
        :param type: The type of the custom field from the following types:
            text – Text
            website – Website
            longtext – Multi-line text
            gpg – GPG Public Key
            number – Number
            radio – Radio Buttons
            checkbox – Checkboxes
            dropdown – Drop Down
            date-us – Date (MM/DD/YYY)
            date-eur – Date (DD/MM/YYYY)
            birthday-us – Birthday (MM/DD)
            birthday-eur – Birthday (DD/MM)
            json – JSON value for custom rendering
            option – Option
        :param group - If the type is 'option' then you also need to specify the parent element ID
        :param group_template – Template for the group element. If not set, then values of the elements are joined with commas
        :param visible – if not visible then the subscriber can not view or modify this value at the profile page
        :return: A dict of the custom field
        """
        # check if type is valid
        valid_types = [
            "text",
            "website",
            "longtext",
            "gpg",
            "number",
            "radio",
            "checkbox",
            "dropdown",
            "date-us",
            "date-eur",
            "birthday-us",
            "birthday-eur",
            "json",
            "option",
        ]
        if type not in valid_types:
            raise ValueError("Invalid type. Valid types are: " + ", ".join(valid_types))

        if type == "option" and group == "":
            raise ValueError("You must specify the parent element ID for type 'option'")

        url = self.api_url + "/api/field/" + list_id + "?access_token=" + self.api_token
        data = {
            "NAME": name,
            "TYPE": type,
            "GROUP": group,
            "GROUP_TEMPLATE": group_template,
            "VISIBLE": "yes" if visible else "no",
        }
        return requests.post(url, data=data)

    @check_response
    def get_blacklist(
        self, start: int = 0, limit: int = 10000, search: str = ""
    ) -> dict:
        """Get blacklisted emails

        :param start: Start position (optional, default 0)
        :param limit: limit emails count in response (optional, default 10000)
        :param search: filter by part of email (optional, default "")
        :return: A dict of blacklisted emails
        """
        url = (
            self.api_url
            + "/api/blacklist/get?access_token="
            + self.api_token
            + "&start="
            + str(start)
            + "&limit="
            + str(limit)
            + "&search="
            + search
        )
        return requests.get(url)

    @validate_email
    @check_response
    def add_to_blacklist(self, email: str) -> dict:
        """Add email to blacklist

        :param email: The email address
        :return: A dict of the blacklisted email
        """
        url = self.api_url + "/api/blacklist/add?access_token=" + self.api_token
        data = {"EMAIL": email}
        return requests.post(url, data=data)

    @validate_email
    @check_response
    def delete_from_blacklist(self, email: str) -> dict:
        """Delete email from blacklist

        :param email: The email address
        :return: A dict of the blacklisted email
        """

        url = self.api_url + "/api/blacklist/delete?access_token=" + self.api_token
        data = {"EMAIL": email}
        return requests.post(url, data=data)

    @validate_email
    @check_response
    def get_lists(self, email: str) -> dict:
        """Retrieve the lists that the user with :email has subscribed to.

        :param email: The email address
        :return: A dict of the lists
        """
        url = self.api_url + "/api/lists/" + email + "?access_token=" + self.api_token
        return requests.get(url)

    @check_response
    def get_lists_by_namespace(self, namespace_id: str) -> dict:
        """Retrieve the lists that the namespace with :namespace_id has.

        :param namespace_id: The namespace id
        :return: A dict of the lists
        """
        url = (
            self.api_url
            + "/api/lists-by-namespace/"
            + namespace_id
            + "?access_token="
            + self.api_token
        )
        return requests.get(url)

    @check_response
    def create_list(
        self,
        namespace: str,
        unsubscription_mode: int,
        name: str = "",
        description: str = "",
        contact_email: str = "",
        homepage: str = "",
        fieldwizard: str = "",
        send_configuration: bool = True,
        public_subscribe: bool = True,
        listunsubscribe_disabled: bool = False,
    ) -> dict:
        """Create a new list of subscribers

        :param namespace: Namespace (required)
        :param unsubscription_mode: Unsubscription (required):
            0 - One-step (i.e. no email with confirmation link)
            1 - One-step with unsubscription form (i.e. no email with confirmation link)
            2 - Two-step (i.e. an email with confirmation link will be sent)
            3 - Two-step with unsubscription form (i.e. an email with confirmation link will be sent)
            4 - Manual (i.e. unsubscription has to be performed by the list administrator)
        :param name: Name
        :param description: Description
        :param contact_email: Contact email
        :param homepage: Homepage
        :param fieldwizard: Representation of subscriber's name:
            none - Empty / Custom (no fields)
            full_name - Name (one field)
            first_last_name - First name and Last name (two fields)
        :param send_configuration: send configuration
        :param public_subscribe: Allow public users to subscribe themselves
        :param listunsubscribe_disabled: Do not send List-Unsubscribe headers
        :return: A dict of the created list
        """
        # check unsubscription_mode is valid
        if unsubscription_mode not in [0, 1, 2, 3, 4]:
            raise ValueError("Invalid unsubscription_mode")
        # check fieldwizard is valid
        if fieldwizard not in ["", "full_name", "first_last_name"]:
            raise ValueError("Invalid fieldwizard")

        url = self.api_url + "/api/list?access_token=" + self.api_token
        data = {
            "NAMESPACE": namespace,
            "UNSUBSCRIPTION_MODE": unsubscription_mode,
            "NAME": name,
            "DESCRIPTION": description,
            "CONTACT_EMAIL": contact_email,
            "HOMEPAGE": homepage,
            "FIELDWIZARD": fieldwizard,
            "SEND_CONFIGURATION": int(send_configuration),
            "PUBLIC_SUBSCRIBE": int(public_subscribe),
            "LISTUNSUBSCRIBE_DISABLED": int(listunsubscribe_disabled),
        }
        return requests.post(url, data=data)

    @check_response
    def delete_list(self, list_id: str) -> dict:
        """Delete a list of subscribers.

        :param list_id: The list id
        :return: A dict of the deleted list
        """
        url = self.api_url + "/api/list/" + list_id + "?access_token=" + self.api_token
        return requests.delete(url)

    @check_response
    def fetch_rss(self, campaign_cid: str) -> dict:
        """Forces the RSS feed check to immediately check the campaign with the given CID (in :campaign_cid). It works only for RSS campaigns.

        :param campaign_cid: The campaign cid
        :return: A dict of the campaign
        """
        url = (
            self.api_url
            + "/api/rss/fetch/"
            + campaign_cid
            + "?access_token="
            + self.api_token
        )
        return requests.get(url)

    @validate_email
    @check_response
    def send_email_by_template(
        self,
        email: str,
        template_id: int = 1,
        tags: dict = {},
        send_configuration_id: int = 0,
        subject: str = "",
        attachments: list = [],
    ) -> dict:
        """Send single email by template with given templateId

        :param email: The email address
        :param template_id: The template id
        :param tags: Map of template variables to replace
        :send_configuration_id: ID of configuration used to create mailer instance. If omitted, the default system send configuration is used.
        :subject: Subject of the email
        :attachments: List of attachments (format as consumed by nodemailer)
        :return: A dict of the campaign
        """
        url = (
            self.api_url
            + "/api/templates/"
            + template_id
            + "/send?access_token="
            + self.api_token
        )
        data = {
            "EMAIL": email,
            "TAGS": tags,
            "SEND_CONFIGURATION_ID": send_configuration_id,
            "SUBJECT": subject,
            "ATTACHMENTS": attachments,
        }
        return requests.post(url, data=data)
