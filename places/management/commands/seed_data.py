import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from places.models import Place
from reviews.models import Review

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with 20 Coimbatore places and random reviews (uses photo_url).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Coimbatore seeding...'))

        # --- Users ---
        users = []
        for i in range(1, 4):
            username = f'user{i}'
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                user.set_password('password')
                user.save()
            users.append(user)
        owner = users[0]
        self.stdout.write(self.style.SUCCESS(f'Users ready: {", ".join([u.username for u in users])}'))

        # --- Clear old data ---
        Review.objects.all().delete()
        Place.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing Place and Review data.'))

        # --- 20 Coimbatore places (approx lat/lon around Coimbatore) ---
        places_data = [
            # Food places
            {'name': 'Annapoorna Gowrishankar', 'type': 'food', 'sub_type': 'mess', 'address': 'Peelamedu, Coimbatore', 'lat': 11.0315, 'lon': 77.0160, 'price': 'average', 'tags': 'south indian,vegetarian,family', 'photo_url': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1974'},
            {'name': 'Sree Subbu Mess', 'type': 'food', 'sub_type': 'mess', 'address': 'Near CIT Campus, Coimbatore', 'lat': 11.0275, 'lon': 77.0235, 'price': 'economical', 'tags': 'chettinad,non-veg,students', 'photo_url': 'https://images.unsplash.com/photo-1552566626-52f8b828add9?q=80&w=2070'},
            {'name': 'The French Door Bakery', 'type': 'food', 'sub_type': 'bakery', 'address': 'R S Puram West, Coimbatore', 'lat': 11.0055, 'lon': 76.9558, 'price': 'premium', 'tags': 'cafe,dessert,romantic', 'photo_url': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=2047'},
            {'name': 'KR Bakes', 'type': 'food', 'sub_type': 'bakery', 'address': 'Avinashi Road, Coimbatore', 'lat': 11.0250, 'lon': 77.0230, 'price': 'economical', 'tags': 'snacks,bakery,quick-bites', 'photo_url': 'https://images.unsplash.com/photo-1563502299833-258abbc6522a?q=80&w=1974'},
            {'name': 'Bird on Tree - Rooftop', 'type': 'food', 'sub_type': 'mess', 'address': 'Race Course, Coimbatore', 'lat': 11.0027, 'lon': 76.9796, 'price': 'premium', 'tags': 'continental,fine-dining,rooftop', 'photo_url': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=2070'},

            # Street food / quick bites
            {'name': 'Rama Mess & Tiffins', 'type': 'food', 'sub_type': 'stall', 'address': 'Town Hall Road, Coimbatore', 'lat': 11.0168, 'lon': 76.9550, 'price': 'economical', 'tags': 'tiffin,breakfast,local', 'photo_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=1974'},
            {'name': 'Kovai Idli Stall', 'type': 'food', 'sub_type': 'stall', 'address': 'RS Puram Market, Coimbatore', 'lat': 11.0060, 'lon': 76.9565, 'price': 'economical', 'tags': 'idli,sambar,breakfast', 'photo_url': 'https://images.unsplash.com/photo-1541542684-6f4f2b8b7c7a?q=80&w=1974'},
            {'name': 'Cafe 41', 'type': 'food', 'sub_type': 'bakery', 'address': 'Gandhipuram, Coimbatore', 'lat': 11.0128, 'lon': 76.9650, 'price': 'average', 'tags': 'coffee,cafe,work-friendly', 'photo_url': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?q=80&w=1974'},
            {'name': 'Savor Street Bites', 'type': 'food', 'sub_type': 'stall', 'address': 'Township Road, Coimbatore', 'lat': 11.0190, 'lon': 76.9700, 'price': 'economical', 'tags': 'street-food,chaat,quick', 'photo_url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1974'},
            {'name': 'Green Leaf Cafe', 'type': 'food', 'sub_type': 'bakery', 'address': 'Peelamedu, Coimbatore', 'lat': 11.0312, 'lon': 77.0165, 'price': 'average', 'tags': 'healthy,vegan,coffee', 'photo_url': 'https://images.unsplash.com/photo-1498804103079-a6351b050096?q=80&w=1974'},

            # Stay places (hostel/pg/hotel)
            {'name': 'CIT Boys Hostel', 'type': 'stay', 'sub_type': 'hostel', 'address': 'CIT Campus, Coimbatore', 'lat': 11.0270, 'lon': 77.0225, 'price': 'economical', 'tags': 'students,on-campus,budget', 'photo_url': 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?q=80&w=2070'},
            {'name': 'Fairfield by Marriott Coimbatore', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Avinashi Road, Coimbatore', 'lat': 11.0300, 'lon': 77.0400, 'price': 'premium', 'tags': 'luxury,business,airport-hotel', 'photo_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070'},
            {'name': 'Sri Krishna PG for Gents', 'type': 'stay', 'sub_type': 'pg', 'address': 'Hope College, Peelamedu, Coimbatore', 'lat': 11.0320, 'lon': 77.0175, 'price': 'average', 'tags': 'students,working-professionals,affordable', 'photo_url': 'https://images.unsplash.com/photo-1590490360182-c33d57733427?q=80&w=1974'},
            {'name': 'The Residency Towers', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Avinashi Road, Coimbatore', 'lat': 11.0163, 'lon': 76.9936, 'price': 'premium', 'tags': '5-star,luxury,rooftop-pool', 'photo_url': 'https://images.unsplash.com/photo-1542314831-068cd1dbb5eb?q=80&w=2070'},
            {'name': 'Le Meridien Coimbatore', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Neelambur, Coimbatore', 'lat': 11.0664, 'lon': 77.0853, 'price': 'premium', 'tags': 'luxury,spa,modern', 'photo_url': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?q=80&w=1949'},

            # More local places to reach 20
            {'name': 'Textile Street Diner', 'type': 'food', 'sub_type': 'mess', 'address': 'RS Puram, Coimbatore', 'lat': 11.0090, 'lon': 76.9580, 'price': 'average', 'tags': 'local,comfort-food,family', 'photo_url': 'https://images.unsplash.com/photo-1525755662778-989d0524087e?q=80&w=1974'},
            {'name': 'Nilgiri Guest House', 'type': 'stay', 'sub_type': 'hotel', 'address': 'Gandhipuram, Coimbatore', 'lat': 11.0145, 'lon': 76.9667, 'price': 'average', 'tags': 'budget,central,clean', 'photo_url': 'https://images.unsplash.com/photo-1501117716987-c8e28f30b3b8?q=80&w=1974'},
            {'name': 'Campus Rental Rooms', 'type': 'stay', 'sub_type': 'rental', 'address': 'Near Hope College, Coimbatore', 'lat': 11.0310, 'lon': 77.0158, 'price': 'economical', 'tags': 'rentals,students,short-term', 'photo_url': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=1974'},
            {'name': 'Old Town Sweets', 'type': 'food', 'sub_type': 'stall', 'address': 'Town Hall, Coimbatore', 'lat': 11.0160, 'lon': 76.9555, 'price': 'economical', 'tags': 'sweets,dessert,local', 'photo_url': 'https://images.unsplash.com/photo-1545126468-7f33f3e1d7ea?q=80&w=1974'},
        ]

        created_places = []
        for pd in places_data:
            place = Place.objects.create(
                name=pd['name'],
                type=pd['type'],
                sub_type=pd['sub_type'],
                address=pd['address'],
                latitude=pd['lat'],
                longitude=pd['lon'],
                price_level=pd['price'],
                description=f"A popular spot in Coimbatore known for its {('great food' if pd['type']=='food' else 'comfortable stay')}.",
                tags=pd['tags'],
                photo_url=pd['photo_url'], 
                is_approved=True,
                average_rating=round(random.uniform(3.5, 5.0), 1),
                added_by=owner
            )
            created_places.append(place)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_places)} places.'))

        review_comments = [
            "Absolutely fantastic! A must-visit.",
            "Good, but could be better. The service was a bit slow.",
            "An average experience. Nothing too special.",
            "Loved the ambiance and the quality. Will definitely come back.",
            "Overpriced for what it is. I've had better."
        ]

        reviews = []
        for place in created_places:
            for _ in range(random.randint(1, 4)): 
                rev = Review(
                    place=place,
                    user=random.choice(users),
                    rating=random.randint(3, 5),
                    comment=random.choice(review_comments)
                )
                reviews.append(rev)

        Review.objects.bulk_create(reviews)
        self.stdout.write(self.style.SUCCESS(f'Added {len(reviews)} reviews.'))
        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
