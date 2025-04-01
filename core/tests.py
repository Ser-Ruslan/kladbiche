from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Cemetery, Burial, UserNote, FavoriteBurial, BurialRequest


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        self.cemetery = Cemetery.objects.create(
            name='Тестовое кладбище',
            latitude=52.033635,
            longitude=113.501049,
            description='Описание тестового кладбища'
        )
        self.burial = Burial.objects.create(
            cemetery=self.cemetery,
            full_name='Иванов Иван Иванович',
            birth_date='1950-01-01',
            death_date='2020-01-01',
            latitude=52.033645,
            longitude=113.501059,
            admin_description='Описание захоронения'
        )

    def test_cemetery_creation(self):
        self.assertEqual(self.cemetery.name, 'Тестовое кладбище')
        self.assertEqual(self.cemetery.latitude, 52.033635)
        self.assertEqual(self.cemetery.longitude, 113.501049)

    def test_burial_creation(self):
        self.assertEqual(self.burial.full_name, 'Иванов Иван Иванович')
        self.assertEqual(self.burial.birth_date.strftime('%Y-%m-%d'), '1950-01-01')
        self.assertEqual(self.burial.death_date.strftime('%Y-%m-%d'), '2020-01-01')
        self.assertEqual(self.burial.cemetery, self.cemetery)

    def test_user_note(self):
        note = UserNote.objects.create(
            user=self.user,
            burial=self.burial,
            text='Тестовая заметка'
        )
        self.assertEqual(note.text, 'Тестовая заметка')
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.burial, self.burial)

    def test_favorite_burial(self):
        favorite = FavoriteBurial.objects.create(
            user=self.user,
            burial=self.burial
        )
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.burial, self.burial)

    def test_burial_request(self):
        request = BurialRequest.objects.create(
            user=self.user,
            cemetery=self.cemetery,
            full_name='Петров Петр Петрович',
            birth_date='1960-01-01',
            death_date='2021-01-01',
            latitude=52.033655,
            longitude=113.501069,
            description='Описание запроса',
            status='pending'
        )
        self.assertEqual(request.full_name, 'Петров Петр Петрович')
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.user, self.user)


class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        self.cemetery = Cemetery.objects.create(
            name='Тестовое кладбище',
            latitude=52.033635,
            longitude=113.501049,
            description='Описание тестового кладбища'
        )
        self.burial = Burial.objects.create(
            cemetery=self.cemetery,
            full_name='Иванов Иван Иванович',
            birth_date='1950-01-01',
            death_date='2020-01-01',
            latitude=52.033645,
            longitude=113.501059,
            admin_description='Описание захоронения'
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')

    def test_burial_detail_view(self):
        response = self.client.get(reverse('burial_detail', args=[self.burial.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'burial_detail.html')
        self.assertContains(response, 'Иванов Иван Иванович')

    def test_login_required_views(self):
        # Проверяем страницы, требующие авторизации
        profile_url = reverse('user_profile')
        
        # Без авторизации
        response = self.client.get(profile_url)
        self.assertNotEqual(response.status_code, 200)
        
        # С авторизацией
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')

    def test_admin_views(self):
        admin_panel_url = reverse('admin_panel')
        
        # Обычный пользователь
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(admin_panel_url)
        self.assertNotEqual(response.status_code, 200)
        
        # Администратор
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(admin_panel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_panel.html')


class APITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        self.cemetery = Cemetery.objects.create(
            name='Тестовое кладбище',
            latitude=52.033635,
            longitude=113.501049,
            description='Описание тестового кладбища'
        )
        self.burial = Burial.objects.create(
            cemetery=self.cemetery,
            full_name='Иванов Иван Иванович',
            birth_date='1950-01-01',
            death_date='2020-01-01',
            latitude=52.033645,
            longitude=113.501059,
            admin_description='Описание захоронения'
        )

    def test_get_burials(self):
        url = reverse('burial-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_burials(self):
        url = reverse('burial-search')
        response = self.client.get(url, {'query': 'Иванов'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Поиск с отсутствующим именем
        response = self.client.get(url, {'query': 'Петров'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_favorite_burial(self):
        self.client.force_authenticate(user=self.user)
        
        url = reverse('favorites-toggle')
        response = self.client.post(url, {'burial_id': self.burial.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_favorite'], True)
        
        # Проверка добавления в избранное
        favorites = FavoriteBurial.objects.filter(user=self.user, burial=self.burial)
        self.assertEqual(favorites.count(), 1)
        
        # Повторный запрос должен удалить из избранного
        response = self.client.post(url, {'burial_id': self.burial.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_favorite'], False)
        
        # Проверка удаления из избранного
        favorites = FavoriteBurial.objects.filter(user=self.user, burial=self.burial)
        self.assertEqual(favorites.count(), 0)
