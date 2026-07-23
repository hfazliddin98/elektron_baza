from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from devices.models import Qurilma
from repairs.models import TamirYozuvi

from .models import AmalTarixi
from .permissions import ADMIN, rol_kerak
from .utils import amal_yoz

Holat = TamirYozuvi.Holat
JARAYONDAGI = [Holat.YANGI, Holat.QABUL, Holat.TASHXIS, Holat.TAMIRDA, Holat.TAYYOR]


class KirishView(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class ChiqishView(auth_views.LogoutView):
    next_page = reverse_lazy('login')


class ParolOzgartirishView(auth_views.PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('parol_tayyor')

    def form_valid(self, form):
        javob = super().form_valid(form)
        amal_yoz(self.request.user, AmalTarixi.Amal.PAROL, request=self.request)
        messages.success(self.request, "Parol muvaffaqiyatli o'zgartirildi.")
        return javob


class ParolTayyorView(auth_views.PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'


def home(request):
    """Bosh sahifa: kirgan foydalanuvchi o'z paneliga yo'naltiriladi."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """Har bir rol uchun o'z paneli."""
    user = request.user
    kontekst = {}

    if user.is_admin or user.is_operator:
        kontekst.update(
            yangi_murojaatlar=TamirYozuvi.objects.filter(holat=Holat.YANGI).count(),
            navbatda=TamirYozuvi.objects.filter(holat=Holat.QABUL, usta__isnull=True).count(),
            tamirda=TamirYozuvi.objects.filter(holat__in=[Holat.TASHXIS, Holat.TAMIRDA]).count(),
            tayyor=TamirYozuvi.objects.filter(holat=Holat.TAYYOR).count(),
            tasdiq_kutmoqda=TamirYozuvi.objects.filter(
                turi=TamirYozuvi.Turi.OZI, tasdiq_holati=TamirYozuvi.Tasdiq.KUTILMOQDA,
            ).count(),
            qurilmalar_soni=Qurilma.objects.count(),
        )

    if user.is_usta:
        usta = user.usta_profili
        kontekst['usta'] = usta
        if usta:
            meniki = TamirYozuvi.objects.filter(usta=usta)
            kontekst.update(
                meniki_aktiv=meniki.filter(holat__in=[Holat.TASHXIS, Holat.TAMIRDA]).count(),
                meniki_tayyor=meniki.filter(holat=Holat.TAYYOR).count(),
                menga_soralgan=TamirYozuvi.objects.filter(
                    tanlangan_usta=usta, holat=Holat.QABUL, usta__isnull=True,
                ).count(),
                navbat=TamirYozuvi.objects.filter(
                    holat=Holat.QABUL, usta__isnull=True, tanlangan_usta__isnull=True,
                ).count(),
                reyting=meniki.filter(baho__isnull=False).aggregate(o=Avg('baho'))['o'],
            )

    if user.is_xodim:
        xodim = user.xodim_profili
        kontekst['xodim'] = xodim
        if xodim:
            meniki = TamirYozuvi.objects.filter(xodim=xodim)
            kontekst.update(
                mening_qurilmalarim=Qurilma.objects.filter(xodim=xodim).count(),
                jarayonda=meniki.filter(holat__in=JARAYONDAGI).count(),
                baholanmagan=meniki.filter(holat=Holat.TOPSHIRILDI, baho__isnull=True).count(),
                ozi_tasdiq_kutmoqda=meniki.filter(
                    turi=TamirYozuvi.Turi.OZI, tasdiq_holati=TamirYozuvi.Tasdiq.KUTILMOQDA,
                ).count(),
            )

    if user.is_rahbariyat or user.is_admin:
        kontekst.update(
            jami_murojaatlar=TamirYozuvi.objects.count(),
            tugatilgan=TamirYozuvi.objects.filter(holat=Holat.TOPSHIRILDI).count(),
            ortacha_baho=TamirYozuvi.objects.filter(baho__isnull=False)
            .aggregate(o=Avg('baho'))['o'],
        )

    return render(request, 'accounts/dashboard.html', kontekst)


@rol_kerak(ADMIN)
def amal_tarixi(request):
    """Audit log — faqat admin uchun."""
    yozuvlar = AmalTarixi.objects.select_related('user')

    q = request.GET.get('q', '').strip()
    amal = request.GET.get('amal', '')
    if q:
        yozuvlar = yozuvlar.filter(Q(user__username__icontains=q) | Q(obyekt__icontains=q))
    if amal:
        yozuvlar = yozuvlar.filter(amal=amal)

    sahifa = Paginator(yozuvlar, 50).get_page(request.GET.get('page'))
    return render(request, 'accounts/amal_tarixi.html', {
        'sahifa': sahifa,
        'q': q,
        'tanlangan_amal': amal,
        'amallar': AmalTarixi.Amal.choices,
    })
