from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Place
from .forms import AddPlaceForm
from reviews.forms import AddReviewForm, ReviewFormForDetailPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        trending_places = Place.objects.filter(is_approved=True).order_by('-average_rating')[:10]
        nearby_places = Place.objects.filter(is_approved=True).order_by('?')[:10]
        recommendations = Place.objects.filter(is_approved=True, type='food').order_by('?')[:10]

        context = {
            'trending_places': trending_places,
            'nearby_places': nearby_places,
            'recommendations': recommendations,
        }
        return render(request, 'places/home.html', context)


class SearchView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        locations = request.GET.getlist('location')
        min_ratings = request.GET.getlist('min_rating')
        prices = request.GET.getlist('price')
        types = request.GET.getlist('type')

        results = Place.objects.filter(is_approved=True)
        active_filters = {}
        
        price_map = {
            'economical': 'Budget Friendly',
            'average': 'Affordable',
            'premium': 'Costly'
        }
        
        location_map = {
            'peelamedu': 'Peelamedu',
            'ram_nagar': 'Ram Nagar',
            'saibaba_colony': 'Saibaba Colony',
            'singanallur': 'Singanallur',
            'gandhipuram': 'Gandhipuram',
            'hopes': 'Hope College',
        }

        if query:
            results = results.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) | 
                Q(tags__icontains=query)
            )
            active_filters['q'] = f'Search: "{query}"'
        
        if locations:
            location_query = Q()
            for loc in locations:
                location_query |= Q(address__icontains=location_map.get(loc, loc))
            results = results.filter(location_query)

            loc_tags = [location_map.get(loc, loc) for loc in locations]
            active_filters['location'] = f"Location: {', '.join(loc_tags)}"

        if min_ratings:
            lowest_rating = min(float(r) for r in min_ratings)
            results = results.filter(average_rating__gte=lowest_rating)
            active_filters['min_rating'] = f'{int(lowest_rating)}+ Stars'

        if prices:
            results = results.filter(price_level__in=prices)
            price_tags = [price_map.get(p, p) for p in prices]
            active_filters['price'] = f"Budget: {', '.join(price_tags)}"
            
        if types:
            results = results.filter(type__in=types)
            active_filters['type'] = f"Type: {', '.join(types).title()}"

        context = {
            'results': results,
            'active_filters': active_filters,
            'q': query,
            'locations': locations,
            'min_ratings': min_ratings,
            'prices': prices,
            'types': types,
        }
        return render(request, 'places/search.html', context)


class AddPlaceView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddPlaceForm()
        return render(request, 'places/add_place.html', {'form': form})

    def post(self, request):
        form = AddPlaceForm(request.POST, request.FILES)
        if form.is_valid():
            place = form.save(commit=False)

            if 'photo' in request.FILES:
                place.photo = request.FILES['photo']

            place.added_by = request.user
            place.save()

            return redirect('places:place_detail', pk=place.pk) 

        return render(request, 'places/add_place.html', {'form': form})


class AddReviewView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddReviewForm()
        return render(request, 'places/add_review.html', {'form': form})

    def post(self, request):
        form = AddReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()

            return redirect('places:place_detail', pk=review.place.pk)

        return render(request, 'places/add_review.html', {'form': form})


class PlaceDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        review_form = ReviewFormForDetailPage()
        return render(request, 'places/place_detail.html', {
            'place': place,
            'review_form': review_form
        })

    def post(self, request, pk):
        place = get_object_or_404(Place, pk=pk)
        review_form = ReviewFormForDetailPage(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.place = place
            review.save()
            messages.success(request, 'Thank you! Your review has been added.')
            return redirect('places:place_detail', pk=pk)  

        return render(request, 'places/place_detail.html', {
            'place': place,
            'review_form': review_form
        })