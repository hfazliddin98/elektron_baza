"""Diagramma ma'lumoti sahifaga to'g'ri yetib borishini tekshiradi.

`json_script` filtri ma'lumotni o'zi JSON'ga o'giradi — view'dan yana bir marta
JSON matn sifatida uzatilsa, brauzerda diagrammalar bo'sh chiqadi.
"""

import json
import re

from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class DiagrammaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username='a', rol=User.Rol.ADMIN)

    def test_diagramma_malumoti_obyekt_korinishida_uzatiladi(self):
        self.client.force_login(self.admin)
        javob = self.client.get(reverse('hisobot'))

        diagramma = javob.context['diagramma']
        self.assertIsInstance(diagramma, dict, 'json_script uchun lug\'at uzatilishi kerak')
        self.assertIn('oylar', diagramma)
        self.assertEqual(len(diagramma['oylar']), 12)

    def test_sahifadagi_json_brauzerda_ochiladi(self):
        self.client.force_login(self.admin)
        matn = self.client.get(reverse('hisobot')).content.decode()

        mos = re.search(
            r'<script id="diagramma-malumot" type="application/json">(.*?)</script>',
            matn, re.DOTALL,
        )
        self.assertIsNotNone(mos, 'json_script bloki topilmadi')

        malumot = json.loads(mos.group(1).replace('\\u0027', "'"))
        self.assertIsInstance(malumot, dict, 'JSON.parse lug\'at qaytarishi kerak')
        self.assertEqual(len(malumot['oylar']), 12)
        self.assertIn('manba_nomlari', malumot)
