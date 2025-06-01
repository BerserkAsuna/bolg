document.addEventListener('DOMContentLoaded', function() {
    // 加载动漫数据
    fetch('data/A2025_4_animes/A2025_4_animes.json')
    // fetch('data/animes.json')
        .then(response => response.json())
        .then(data => {
            // 生成每天的动漫内容
            for (const day in data) {
                if (data.hasOwnProperty(day) && data[day].length > 0) {
                    const gridElement = document.getElementById(`${day}-grid`);
                    if (gridElement) {
                        data[day].forEach(anime => {
                            const card = createAnimeCard(anime);
                            gridElement.appendChild(card);
                        });
                    }
                }
            }
            
            // 设置默认显示当天的内容
            setActiveDay(getCurrentDay());
        })
        .catch(error => {
            console.error('Error loading anime data:', error);
            // 显示错误信息给用户
            document.querySelector('main').innerHTML = `
                <div class="error-message">
                    <h2>加载数据失败</h2>
                    <p>无法加载动漫数据，请稍后再试。</p>
                </div>
            `;
        });
    
    // 设置选项卡点击事件
    const tabLinks = document.querySelectorAll('.tab-nav a');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const day = this.getAttribute('data-day');
            setActiveDay(day);
        });
    });
});

// 创建动漫卡片
function createAnimeCard(anime) {
    const card = document.createElement('div');
    card.className = 'anime-card';
    
    card.innerHTML = `
        <div class="time">${anime.time}</div>
        <a href="${anime.url}" target="_blank">
            <img src="${anime.image}" alt="${anime.title}">
            <div class="info">
                <h3 class="${anime.isWatch === 'no' ? 'notWatch' : anime.isWatch === 'yes' ? 'watching' : ''}">${anime.title}</h3>
                <span class="episodes">${anime.episodes}</span>
                <span class="${anime.ladder === 'no' ? 'god' : anime.ladder === 'yes' ? 'needLadder' : ''}">${anime.god}</span>
            </div>
        </a>
    `;
    
    return card;
}

// 设置活动标签
function setActiveDay(day) {
    // 移除所有活动类
    document.querySelectorAll('.tab-nav a').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelectorAll('.day-schedule').forEach(section => {
        section.classList.remove('active');
    });
    
    // 添加活动类到选中的标签
    const activeLink = document.querySelector(`.tab-nav a[data-day="${day}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // 显示选中的内容
    const activeContent = document.getElementById(day);
    if (activeContent) {
        activeContent.classList.add('active');
        
        // 检查该日期内容是否为空
        const grid = activeContent.querySelector('.anime-grid');
        if (grid && grid.children.length === 0) {
            grid.innerHTML = '<div class="no-anime-message">今日暂无新番</div>';
        }
    }
}

// 获取当前星期几
function getCurrentDay() {
    const dayMapping = {
        0: 'sunday',
        1: 'monday',
        2: 'tuesday',
        3: 'wednesday',
        4: 'thursday',
        5: 'friday',
        6: 'saturday'
    };
    
    const today = new Date().getDay();
    return dayMapping[today] || 'monday'; // 默认周一
}