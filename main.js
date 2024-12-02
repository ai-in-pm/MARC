const hamburger = document.querySelector(".hamburger-container");
const tabNav = document.querySelector(".tab-nav");
const tabNavList = document.querySelectorAll(".tab-nav li");
const tabList = document.querySelectorAll(".tab-body");
const questions = document.querySelectorAll(".question");
const logoContainer = document.querySelector('.logo-container');
let toggle = false;

hamburger.addEventListener("click", function () {
  const hamburger = document.querySelector(".hamburger");
  const navList = document.querySelector(".nav-list");
  toggle = !toggle;
  let srcHam = "./images/icon-hamburger.svg";
  let srcClose = "./images/icon-close.svg";
  hamburger.src = toggle ? srcClose : srcHam;
  navList.classList.toggle("active");
  logoContainer.classList.toggle('active');
  document.body.style.position = toggle ? 'fixed' : 'static';
});

tabNavList.forEach((item, index, array) => {
  item.addEventListener("click", () => {
    tabNav.querySelector(".active").classList.remove("active");
    item.classList.add("active");

    if (item.classList.contains("one")) {
      tabList[0].classList.add("active");
      tabList[1].classList.remove("active");
    }

    if (item.classList.contains("two")) {
      tabList[1].classList.add("active");
      tabList[0].classList.remove("active");
    }
  });
});

questions.forEach((item) => {
  item.addEventListener("click", () => {
    item.classList.toggle("open");
  });
});

// Dark mode functionality
function createDarkModeToggle() {
  const nav = document.querySelector('.nav-list');
  const darkModeBtn = document.createElement('li');
  darkModeBtn.className = 'nav-item';
  darkModeBtn.innerHTML = `
    <button class="nav-link btn clr1" id="darkModeToggle">
      <span class="mode-text">Dark Mode</span>
    </button>
  `;
  nav.insertBefore(darkModeBtn, nav.firstChild);

  const darkModeToggle = document.getElementById('darkModeToggle');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  
  // Check for saved theme preference or use system preference
  const currentTheme = localStorage.getItem('theme') || 
    (prefersDarkScheme.matches ? 'dark' : 'light');
  
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateDarkModeButton(currentTheme === 'dark');

  darkModeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateDarkModeButton(!isDark);
  });
}

function updateDarkModeButton(isDark) {
  const modeText = document.querySelector('.mode-text');
  modeText.textContent = isDark ? 'Light Mode' : 'Dark Mode';
}

// Search functionality
function createSearchBar() {
  const header = document.querySelector('.intro');
  const searchContainer = document.createElement('div');
  searchContainer.className = 'search-container';
  searchContainer.innerHTML = `
    <input type="text" id="paperSearch" placeholder="Search papers..." class="search-input">
    <div id="searchResults" class="search-results"></div>
  `;
  header.appendChild(searchContainer);

  const searchInput = document.getElementById('paperSearch');
  searchInput.addEventListener('input', debounce(handleSearch, 300));
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function handleSearch() {
  const searchInput = document.getElementById('paperSearch');
  const searchResults = document.getElementById('searchResults');
  const query = searchInput.value.toLowerCase();

  if (query.length < 2) {
    searchResults.style.display = 'none';
    return;
  }

  // Implement paper search logic here
  // This is a placeholder - you'll need to connect this to your actual paper data
  const results = searchPapers(query);
  displaySearchResults(results);
}

function searchPapers(query) {
  // This is a placeholder - implement actual search logic
  return [];
}

function displaySearchResults(results) {
  const searchResults = document.getElementById('searchResults');
  searchResults.style.display = results.length ? 'block' : 'none';
  searchResults.innerHTML = results.map(result => `
    <div class="search-result-item">
      <h4>${result.title}</h4>
      <p>${result.authors}</p>
    </div>
  `).join('');
}

// Chapter Progress Tracking
function initializeProgressTracking() {
  const chapters = document.querySelectorAll('.card');
  const progress = JSON.parse(localStorage.getItem('chapterProgress') || '{}');

  chapters.forEach(chapter => {
    const chapterId = chapter.querySelector('h4')?.textContent;
    if (!chapterId) return;

    // Add progress indicator
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    progressBar.innerHTML = `
      <div class="progress-fill" style="width: ${progress[chapterId] || 0}%"></div>
      <span class="progress-text">${progress[chapterId] || 0}% Complete</span>
    `;
    chapter.appendChild(progressBar);

    // Add complete/reset buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'progress-buttons';
    buttonContainer.innerHTML = `
      <button class="complete-btn ${progress[chapterId] === 100 ? 'completed' : ''}">
        ${progress[chapterId] === 100 ? 'Completed' : 'Mark as Complete'}
      </button>
      <button class="reset-btn">Reset Progress</button>
    `;
    chapter.appendChild(buttonContainer);

    // Add event listeners
    const completeBtn = buttonContainer.querySelector('.complete-btn');
    const resetBtn = buttonContainer.querySelector('.reset-btn');

    completeBtn.addEventListener('click', () => {
      const newProgress = progress[chapterId] === 100 ? 0 : 100;
      updateChapterProgress(chapterId, newProgress);
      completeBtn.textContent = newProgress === 100 ? 'Completed' : 'Mark as Complete';
      completeBtn.classList.toggle('completed', newProgress === 100);
      progressBar.querySelector('.progress-fill').style.width = `${newProgress}%`;
      progressBar.querySelector('.progress-text').textContent = `${newProgress}% Complete`;
    });

    resetBtn.addEventListener('click', () => {
      updateChapterProgress(chapterId, 0);
      completeBtn.textContent = 'Mark as Complete';
      completeBtn.classList.remove('completed');
      progressBar.querySelector('.progress-fill').style.width = '0%';
      progressBar.querySelector('.progress-text').textContent = '0% Complete';
    });
  });
}

function updateChapterProgress(chapterId, value) {
  const progress = JSON.parse(localStorage.getItem('chapterProgress') || '{}');
  progress[chapterId] = value;
  localStorage.setItem('chapterProgress', JSON.stringify(progress));
}

// Update initialization
document.addEventListener('DOMContentLoaded', () => {
  createDarkModeToggle();
  createSearchBar();
  initializeProgressTracking();
});