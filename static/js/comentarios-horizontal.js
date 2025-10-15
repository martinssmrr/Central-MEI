document.addEventListener('DOMContentLoaded', function() {
    const wrapper = document.getElementById('testimonialsScrollWrapper');
    const prevBtn = document.getElementById('testimonialsNavPrev');
    const nextBtn = document.getElementById('testimonialsNavNext');
    const indicators = document.querySelectorAll('.indicator-dot');
    
    if (!wrapper || !prevBtn || !nextBtn) {
        return; // Se não encontrar os elementos, não executa
    }
    
    const slides = wrapper.children;
    const totalSlides = slides.length;
    let currentIndex = 0;
    let slidesToShow = 3; // Número de slides visíveis por vez
    
    // Função para calcular quantos slides mostrar baseado na largura da tela
    function updateSlidesToShow() {
        if (window.innerWidth <= 576) {
            slidesToShow = 1;
        } else if (window.innerWidth <= 768) {
            slidesToShow = 2;
        } else if (window.innerWidth <= 1200) {
            slidesToShow = 2;
        } else {
            slidesToShow = 3;
        }
        
        // Garante que não tentemos mostrar mais slides do que temos
        slidesToShow = Math.min(slidesToShow, totalSlides);
    }
    
    // Função para atualizar a posição do scroll
    function updateSlidePosition() {
        const slideWidth = slides[0].offsetWidth + 20; // Largura + gap
        const translateX = -(currentIndex * slideWidth);
        wrapper.style.transform = `translateX(${translateX}px)`;
        
        // Atualiza botões
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= totalSlides - slidesToShow;
        
        // Atualiza indicadores
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentIndex);
        });
    }
    
    // Função para ir para o slide anterior
    function goToPrevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlidePosition();
        }
    }
    
    // Função para ir para o próximo slide
    function goToNextSlide() {
        if (currentIndex < totalSlides - slidesToShow) {
            currentIndex++;
            updateSlidePosition();
        }
    }
    
    // Função para ir para um slide específico
    function goToSlide(index) {
        currentIndex = Math.min(Math.max(0, index), totalSlides - slidesToShow);
        updateSlidePosition();
    }
    
    // Event listeners
    prevBtn.addEventListener('click', goToPrevSlide);
    nextBtn.addEventListener('click', goToNextSlide);
    
    // Indicadores
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            goToSlide(index);
        });
    });
    
    // Suporte ao teclado
    wrapper.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            goToPrevSlide();
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            goToNextSlide();
        }
    });
    
    // Suporte ao toque (swipe)
    let startX = 0;
    let endX = 0;
    
    wrapper.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
    }, { passive: true });
    
    wrapper.addEventListener('touchmove', function(e) {
        endX = e.touches[0].clientX;
    }, { passive: true });
    
    wrapper.addEventListener('touchend', function(e) {
        const swipeDistance = startX - endX;
        const minSwipeDistance = 50;
        
        if (Math.abs(swipeDistance) > minSwipeDistance) {
            if (swipeDistance > 0) {
                // Swipe para a esquerda - próximo slide
                goToNextSlide();
            } else {
                // Swipe para a direita - slide anterior
                goToPrevSlide();
            }
        }
    }, { passive: true });
    
    // Scroll automático opcional (pode ser ativado/desativado)
    let autoScrollInterval;
    let isAutoScrolling = true;
    
    function startAutoScroll() {
        if (isAutoScrolling && totalSlides > slidesToShow) {
            autoScrollInterval = setInterval(() => {
                if (currentIndex >= totalSlides - slidesToShow) {
                    currentIndex = 0;
                } else {
                    currentIndex++;
                }
                updateSlidePosition();
            }, 3000); // Muda a cada 3 segundos para ver mais rápido
        }
    }
    
    function stopAutoScroll() {
        clearInterval(autoScrollInterval);
    }
    
    // Pausa o auto-scroll quando o mouse está sobre o container
    const container = wrapper.closest('.testimonials-horizontal-container');
    if (container) {
        container.addEventListener('mouseenter', stopAutoScroll);
        container.addEventListener('mouseleave', startAutoScroll);
    }
    
    // Pausa o auto-scroll quando há interação do usuário
    [prevBtn, nextBtn, ...indicators].forEach(element => {
        element.addEventListener('click', () => {
            isAutoScrolling = false;
            stopAutoScroll();
        });
    });
    
    // Atualiza configurações quando a tela é redimensionada
    window.addEventListener('resize', function() {
        updateSlidesToShow();
        
        // Ajusta o currentIndex se necessário
        if (currentIndex >= totalSlides - slidesToShow) {
            currentIndex = Math.max(0, totalSlides - slidesToShow);
        }
        
        updateSlidePosition();
    });
    
    // Verificar se existem depoimentos suficientes para scroll
    if (totalSlides <= 3) {
        // Se há 3 ou menos depoimentos, não ativa o auto-scroll
        isAutoScrolling = false;
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
    }
    
    // Inicialização
    updateSlidesToShow();
    updateSlidePosition();
    
    // Inicia o auto-scroll após 2 segundos
    setTimeout(startAutoScroll, 2000);
    
    // Adiciona acessibilidade com foco no teclado
    wrapper.setAttribute('tabindex', '0');
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', 'Depoimentos de clientes');
    
    // Melhora a acessibilidade dos botões
    prevBtn.setAttribute('aria-describedby', 'testimonials-help');
    nextBtn.setAttribute('aria-describedby', 'testimonials-help');
    
    // Adiciona texto de ajuda para screen readers (opcional)
    const helpText = document.createElement('div');
    helpText.id = 'testimonials-help';
    helpText.className = 'visually-hidden';
    helpText.textContent = 'Use as setas do teclado ou os botões para navegar pelos depoimentos';
    container.appendChild(helpText);
});