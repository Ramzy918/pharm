from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.catalog.models import Order


class Command(BaseCommand):
    help = 'Auto-update order status (simulate shipping after X time)'

    def handle(self, *args, **options):
        # Get orders that are confirmed but not yet shipped
        confirmed_orders = Order.objects.filter(
            status=Order.Status.CONFIRMED,
            auto_shipped_at__isnull=True
        )

        updated_count = 0
        
        for order in confirmed_orders:
            # Check if order has been confirmed for more than 30 minutes
            time_since_confirmation = timezone.now() - order.created_at
            
            if time_since_confirmation >= timedelta(minutes=30):
                # Update status to SHIPPED
                order.status = Order.Status.SHIPPED
                order.auto_shipped_at = timezone.now()
                order.save()
                
                updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Order {order.id} automatically shipped "
                        f"(confirmed {time_since_confirmation.total_seconds()/60:.1f} minutes ago)"
                    )
                )

        # Also check for orders shipped for more than 24 hours and mark as delivered
        shipped_orders = Order.objects.filter(
            status=Order.Status.SHIPPED,
            auto_shipped_at__isnull=False
        )

        delivered_count = 0
        for order in shipped_orders:
            time_since_shipping = timezone.now() - order.auto_shipped_at
            
            if time_since_shipping >= timedelta(hours=24):
                # Update status to DELIVERED
                order.status = Order.Status.DELIVERED
                order.save()
                
                delivered_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Order {order.id} automatically delivered "
                        f"(shipped {time_since_shipping.total_seconds()/3600:.1f} hours ago)"
                    )
                )

        total_updated = updated_count + delivered_count
        
        if total_updated > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nAuto-update completed: {updated_count} orders shipped, "
                    f"{delivered_count} orders delivered"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("No orders to auto-update")
            )
