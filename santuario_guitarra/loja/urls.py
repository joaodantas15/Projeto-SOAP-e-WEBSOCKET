from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('luthieria/', views.luthieria, name='luthieria'),
    path('estudio/', views.estudio, name='estudio'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/limpar/', views.limpar_carrinho, name='limpar_carrinho'),
    path('carrinho/finalizar/', views.finalizar_pedido, name='finalizar_pedido'), # <-- ADICIONE ESTA LINHA
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]