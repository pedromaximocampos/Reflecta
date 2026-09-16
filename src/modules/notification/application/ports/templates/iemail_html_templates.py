from typing import Protocol

from src.modules.notification.application.ports.notifiers.dto import EmailDTO


class IEmailHtmlTemplates(Protocol):

    @staticmethod
    def get_subject_template(dto: EmailDTO) -> str:
        """
        Retrieve the subject template by its name.

        :param dto:

        :return: The subject content of the email template.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    def get_email_template(dto: EmailDTO) -> str:
        """
        Retrieve the HTML email template by its name.

        :param dto:
        :return: The HTML content of the email template.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")