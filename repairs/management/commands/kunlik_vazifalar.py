"""Kuniga bir marta bajariladigan avtomatik vazifalar.

Serverda cron (yoki Windows Task Scheduler) orqali kuniga bir marta ishga
tushiriladi:

    python manage.py kunlik_vazifalar

Bajaradi:
1. Muddati o'tgan (SLA) ta'mirlar haqida adminlarga xabar beradi.
2. Baholanmagan ta'mirlar bo'yicha xodimlarga eslatma yuboradi (3 kundan keyin).
3. 7 kundan beri baholanmaganlarni bahosiz yopadi.
4. Tanlangan usta javob bermagan ishlarni umumiy navbatga qaytaradi.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from repairs import xabarnomalar
from repairs.models import TamirYozuvi


class Command(BaseCommand):
    help = "Kunlik vazifalar: SLA ogohlantirishi, baho eslatmasi va avtoyopish"

    def add_arguments(self, parser):
        parser.add_argument(
            '--quruq', action='store_true',
            help="Hech narsani o'zgartirmasdan, faqat nima bo'lishini ko'rsatadi",
        )

    def handle(self, *args, **options):
        quruq = options['quruq']
        endi = timezone.now()

        # 1. SLA — muddati o'tganlar
        kechikkanlar = list(
            TamirYozuvi.objects.kechikkanlar().select_related('qurilma').order_by('holat_sana')
        )
        if kechikkanlar and not quruq:
            xabarnomalar.sla_ogohlantirish(kechikkanlar)
        self.stdout.write(f"Muddati o'tgan ta'mirlar: {len(kechikkanlar)}")

        # 2. Baho eslatmasi
        eslatma_chegara = endi - timedelta(days=TamirYozuvi.BAHO_ESLATMA_KUN)
        eslatiladiganlar = TamirYozuvi.objects.filter(
            holat=TamirYozuvi.Holat.TOPSHIRILDI, baho__isnull=True, baho_yopilgan=False,
            baho_eslatma_yuborilgan=False, topshirilgan_sana__lt=eslatma_chegara,
        ).select_related('qurilma', 'xodim')

        eslatildi = 0
        for tamir in eslatiladiganlar:
            if not quruq:
                xabarnomalar.baho_eslatmasi(tamir)
                tamir.baho_eslatma_yuborilgan = True
                tamir.save(update_fields=['baho_eslatma_yuborilgan'])
            eslatildi += 1
        self.stdout.write(f'Baho eslatmalari: {eslatildi}')

        # 3. Bahosiz yopish
        yopish_chegara = endi - timedelta(days=TamirYozuvi.BAHO_YOPISH_KUN)
        yopiladiganlar = TamirYozuvi.objects.filter(
            holat=TamirYozuvi.Holat.TOPSHIRILDI, baho__isnull=True, baho_yopilgan=False,
            topshirilgan_sana__lt=yopish_chegara,
        )
        yopildi = yopiladiganlar.count()
        if not quruq:
            yopiladiganlar.update(baho_yopilgan=True)
        self.stdout.write(f'Bahosiz yopilganlar: {yopildi}')

        # 4. Tanlangan usta javob bermaganlarni umumiy navbatga qaytarish
        usta_chegara = endi - timedelta(days=TamirYozuvi.TANLANGAN_USTA_KUN)
        qaytariladiganlar = TamirYozuvi.objects.navbatdagi().filter(
            tanlangan_usta__isnull=False, navbatga_tushgan__lt=usta_chegara,
        ).select_related('qurilma')
        qaytarildi = 0
        for tamir in qaytariladiganlar:
            if not quruq:
                tamir.tanlangan_usta = None
                tamir.save(update_fields=['tanlangan_usta'])
                xabarnomalar.navbatga_tushdi(tamir)
            qaytarildi += 1
        self.stdout.write(f'Umumiy navbatga qaytarilganlar: {qaytarildi}')

        if quruq:
            self.stdout.write(self.style.WARNING("Quruq rejim — hech narsa o'zgartirilmadi."))
        else:
            self.stdout.write(self.style.SUCCESS('Kunlik vazifalar bajarildi.'))
