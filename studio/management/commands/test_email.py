from django.core.management.base import BaseCommand
from decimal import Decimal
from studio.models import Donation, SponsorTier, DonationGoal


class Command(BaseCommand):
    help = 'Test the email system with a sample donation'

    def handle(self, *args, **options):
        self.stdout.write('Creating test donation to test email system...')
        
        # Get a sponsor tier and goal for testing
        tier = SponsorTier.objects.filter(name='gold').first()
        goal = DonationGoal.objects.filter(status='active').first()
        
        # Create a test donation
        test_donation = Donation(
            amount=Decimal('100.00'),
            donor_name='Test User',
            donor_email='test@example.com',
            donation_type='one_time',
            sponsor_tier=tier,
            donation_goal=goal,
            thank_you_sent=False
        )
        
        self.stdout.write('Sending test thank you email...')
        
        # Test the email function
        test_donation.send_thank_you_email()
        
        self.stdout.write(
            self.style.SUCCESS('Test email sent! Check your console output above for the email content.')
        )
        
        # Don't save the test donation to database
        self.stdout.write('Note: Test donation was not saved to database.')
