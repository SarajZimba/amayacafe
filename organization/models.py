from django.db import models
from root.utils import BaseModel, SingletonModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
import environ
env = environ.Env(DEBUG=(bool, False))


class StaticPage(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateField(null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Organization(SingletonModel, BaseModel):
    # basic company details
    org_name = models.CharField(max_length=255)
    org_logo = models.ImageField(
        upload_to="organization/images/", null=True, blank=True
    )
    tax_number = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="PAN/VAT Number"
    )
    website = models.URLField(null=True, blank=True)
    current_fiscal_year = models.CharField(max_length=20)
    start_year = models.IntegerField()
    end_year = models.IntegerField()

    # contact details
    company_contact_number = models.CharField(max_length=255, null=True, blank=True)
    company_contact_email = models.EmailField(null=True, blank=True)
    contact_person_name = models.CharField(max_length=255, null=True, blank=True)
    contact_person_number = models.CharField(max_length=255, null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    company_bank_qr = models.ImageField(
        upload_to="organization/images/", null=True, blank=True
    )

    def __str__(self):
        return self.org_name
    
    def get_fiscal_year(self):
        return f'{self.start_year}-{self.end_year}'


from uuid import uuid4


def get_default_uuid():
    return uuid4().hex


class Branch(BaseModel):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    branch_manager = models.CharField(max_length=255, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    branch_code = models.CharField(
        max_length=255, null=False, blank=False, unique=True, default=get_default_uuid
    )
    is_central = models.BooleanField(default=False, verbose_name='For Central Billing (Web)')

    def __str__(self):
        return f"{self.organization.org_name} - {self.name}"



class Terminal(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal_no = models.PositiveIntegerField()

    def __str__(self):
        return f'Terminal {self.terminal_no} of branch {self.branch.name}'
    

@receiver(post_save, sender=Terminal)
def create_profile(sender, instance, created, **kwargs):
    if created:
        pass
        # create_terminal_sub_ledgers(branch_code=instance.branch.branch_code, terminal_no=instance.terminal_no)

class PrinterSetting(BaseModel):

    PRINTER_LOCATION = (
        ('KITCHEN', "KITCHEN"),
        ("BAR", "BAR")
    )

    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    url = models.CharField(max_length=100, null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    printer_location = models.CharField(max_length=10, choices=PRINTER_LOCATION)

    def __str__(self):
        return f'Printer for terminal {self.terminal.terminal_no}'
    
    class Meta:
        unique_together = 'printer_location', 'terminal',



class Table(BaseModel):
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    table_number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.table_number} table from Terminal {self.terminal.terminal_no}'


class EndDayRecord(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    terminal = models.CharField(max_length=10)
    date = models.DateField()

    def __str__(self):
        return self.branch.name



class MailRecipient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MailSendRecord(models.Model):
    mail_recipient = models.ForeignKey(MailRecipient, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mail_recipient.name


class EndDayDailyReport(BaseModel):
    employee_name = models.CharField(max_length=50)
    net_sales = models.FloatField()
    vat = models.FloatField()
    total_discounts = models.FloatField()
    cash = models.FloatField()
    credit = models.FloatField()
    credit_card = models.FloatField()
    mobile_payment = models.FloatField()
    complimentary = models.FloatField()
    start_bill = models.CharField(max_length=20)
    end_bill = models.CharField(max_length=20)
    total_void_count = models.IntegerField()
    date_time = models.CharField(max_length=100, null=True)
    food_sale = models.FloatField()
    beverage_sale = models.FloatField()
    others_sale = models.FloatField()
    no_of_guest = models.IntegerField()
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    terminal = models.CharField(max_length=10, null=True)
    total_sale = models.FloatField(default=0)
    created_date = models.DateField(default=datetime.date.today)

    class Meta:
        unique_together = 'created_date', 'start_bill', 'end_bill'

    def __str__(self):
        return 'Report'
    
    def save(self, *args, **kwargs):
        self.total_sale = self.net_sales + self.vat
        return super().save()
    

from .utils import send_mail_to_receipients
from threading import Thread
from datetime import datetime

@receiver(post_save, sender=EndDayDailyReport)
def create_profile(sender, instance, created, **kwargs):
    if created:
        sender = env('EMAIL_HOST_USER')
        mail_list = []
        recipients = MailRecipient.objects.filter(status=True)
        for r in recipients:
            mail_list.append(r.email)
            MailSendRecord.objects.create(mail_recipient=r)
        if mail_list:
            dt_now = datetime.now()
            date_now = dt_now.date()
            time_now = dt_now.time().strftime('%I:%M %p')
            org = Organization.objects.first().org_name
            report_data = {
                'org_name':org,
                'date_now': date_now,
                'time_now': time_now,
                'total_sale': instance.total_sale,
                'date_time':instance.date_time,
                'employee_name': instance.employee_name,
                'net_sales': instance.net_sales,
                'vat': instance.vat,  
                'total_discounts': instance.total_discounts,
                'cash': instance.cash,
                'credit': instance.credit,
                'credit_card': instance.credit_card,
                'mobile_payment': instance.mobile_payment,
                'complimentary': instance.complimentary,
                'start_bill': instance.start_bill,
                'end_bill': instance.end_bill,
                'total_void_count': instance.total_void_count,
                'food_sale': instance.food_sale,
                'beverage_sale': instance.beverage_sale,
                'others_sale': instance.others_sale,
                'no_of_guest': instance.no_of_guest,
                'branch': instance.branch.name,
                'terminal': instance.terminal,
            }
            Thread(target=send_mail_to_receipients, args=(report_data, mail_list, sender)).start()