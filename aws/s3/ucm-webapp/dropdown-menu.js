class DropdownMenu extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.isOpen = false;
    this.selectedValue = '';
    this.selectedText = '';
  }

  static get observedAttributes() {
    return ['placeholder', 'disabled', 'multiple', 'searchable'];
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.loadOptions();
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  get placeholder() {
    return this.getAttribute('placeholder') || 'Select an option';
  }

  get disabled() {
    return this.hasAttribute('disabled');
  }

  get multiple() {
    return this.hasAttribute('multiple');
  }

  get searchable() {
    return this.hasAttribute('searchable');
  }

  loadOptions() {
    const options = Array.from(this.querySelectorAll('option')).map(option => ({
      value: option.value,
      text: option.textContent.trim(),
      selected: option.hasAttribute('selected'),
      disabled: option.hasAttribute('disabled')
    }));

    this.options = options;
    this.renderOptions();
    
    // Set initial selection
    const selectedOption = options.find(opt => opt.selected);
    if (selectedOption && !this.multiple) {
      this.selectedValue = selectedOption.value;
      this.selectedText = selectedOption.text;
      this.shadowRoot.querySelector('.dropdown-trigger span').textContent = selectedOption.text;
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: inline-block;
          position: relative;
          width: 200px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .dropdown-container {
          position: relative;
        }

        .dropdown-trigger {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 12px;
          border: 2px solid #e1e5e9;
          border-radius: 6px;
          background: white;
          cursor: pointer;
          transition: all 0.2s ease;
          min-height: 20px;
        }

        .dropdown-trigger:hover:not(.disabled) {
          border-color: #0066cc;
        }

        .dropdown-trigger.open {
          border-color: #0066cc;
          box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
        }

        .dropdown-trigger.disabled {
          background: #f5f5f5;
          cursor: not-allowed;
          opacity: 0.6;
        }

        .dropdown-trigger span {
          color: #333;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-trigger span.placeholder {
          color: #666;
        }

        .dropdown-arrow {
          width: 0;
          height: 0;
          border-left: 4px solid transparent;
          border-right: 4px solid transparent;
          border-top: 4px solid #666;
          transition: transform 0.2s ease;
          margin-left: 8px;
          flex-shrink: 0;
        }

        .dropdown-trigger.open .dropdown-arrow {
          transform: rotate(180deg);
        }

        .dropdown-menu {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 2px solid #e1e5e9;
          border-top: none;
          border-radius: 0 0 6px 6px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          max-height: 200px;
          overflow-y: auto;
          z-index: 1000;
          display: none;
        }

        .dropdown-menu.open {
          display: block;
        }

        .search-input {
          width: 100%;
          padding: 8px 12px;
          border: none;
          border-bottom: 1px solid #e1e5e9;
          outline: none;
          font-size: 14px;
        }

        .dropdown-option {
          padding: 8px 12px;
          cursor: pointer;
          transition: background-color 0.15s ease;
          display: flex;
          align-items: center;
        }

        .dropdown-option:hover:not(.disabled) {
          background-color: #f0f8ff;
        }

        .dropdown-option.selected {
          background-color: #0066cc;
          color: white;
        }

        .dropdown-option.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .dropdown-option.hidden {
          display: none;
        }

        .checkbox {
          margin-right: 8px;
          width: 16px;
          height: 16px;
        }

        .no-options {
          padding: 8px 12px;
          color: #666;
          font-style: italic;
          text-align: center;
        }

        /* Multiple selection tags */
        .selected-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
          margin-bottom: 4px;
        }

        .selected-tag {
          background: #0066cc;
          color: white;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 12px;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .tag-remove {
          cursor: pointer;
          font-weight: bold;
        }
      </style>

      <div class="dropdown-container">
        <div class="dropdown-trigger ${this.disabled ? 'disabled' : ''}" 
             tabindex="${this.disabled ? '-1' : '0'}" 
             role="combobox" 
             aria-expanded="false"
             aria-haspopup="listbox">
          ${this.multiple ? '<div class="selected-tags"></div>' : ''}
          <span class="placeholder">${this.placeholder}</span>
          <div class="dropdown-arrow"></div>
        </div>
        
        <div class="dropdown-menu" role="listbox">
          ${this.searchable ? '<input type="text" class="search-input" placeholder="Search options...">' : ''}
          <div class="options-container"></div>
        </div>
      </div>
    `;
  }

  renderOptions() {
    const container = this.shadowRoot.querySelector('.options-container');
    if (!container || !this.options) return;

    if (this.options.length === 0) {
      container.innerHTML = '<div class="no-options">No options available</div>';
      return;
    }

    container.innerHTML = this.options.map(option => `
      <div class="dropdown-option ${option.selected ? 'selected' : ''} ${option.disabled ? 'disabled' : ''}" 
           data-value="${option.value}" 
           role="option" 
           aria-selected="${option.selected}">
        ${this.multiple ? `<input type="checkbox" class="checkbox" ${option.selected ? 'checked' : ''} ${option.disabled ? 'disabled' : ''}>` : ''}
        <span>${option.text}</span>
      </div>
    `).join('');
  }

  setupEventListeners() {
    const trigger = this.shadowRoot.querySelector('.dropdown-trigger');
    const menu = this.shadowRoot.querySelector('.dropdown-menu');
    const searchInput = this.shadowRoot.querySelector('.search-input');

    // Toggle dropdown
    trigger.addEventListener('click', (e) => {
      if (this.disabled) return;
      e.stopPropagation();
      this.toggle();
    });

    // Keyboard navigation
    trigger.addEventListener('keydown', (e) => {
      if (this.disabled) return;
      
      switch (e.key) {
        case 'Enter':
        case ' ':
          e.preventDefault();
          this.toggle();
          break;
        case 'Escape':
          this.close();
          break;
        case 'ArrowDown':
          e.preventDefault();
          if (!this.isOpen) {
            this.open();
          } else {
            this.focusNextOption();
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          if (this.isOpen) {
            this.focusPreviousOption();
          }
          break;
      }
    });

    // Option selection
    menu.addEventListener('click', (e) => {
      const option = e.target.closest('.dropdown-option');
      if (option && !option.classList.contains('disabled')) {
        this.selectOption(option);
      }
    });

    // Search functionality
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterOptions(e.target.value);
      });

      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.close();
          trigger.focus();
        }
      });
    }

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!this.contains(e.target)) {
        this.close();
      }
    });

    // Handle tag removal for multiple selection
    if (this.multiple) {
      const tagsContainer = this.shadowRoot.querySelector('.selected-tags');
      tagsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('tag-remove')) {
          const value = e.target.parentElement.dataset.value;
          this.deselectOption(value);
        }
      });
    }
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    if (this.disabled) return;
    
    this.isOpen = true;
    const trigger = this.shadowRoot.querySelector('.dropdown-trigger');
    const menu = this.shadowRoot.querySelector('.dropdown-menu');
    const searchInput = this.shadowRoot.querySelector('.search-input');

    trigger.classList.add('open');
    trigger.setAttribute('aria-expanded', 'true');
    menu.classList.add('open');

    if (searchInput) {
      setTimeout(() => searchInput.focus(), 0);
    }

    this.dispatchEvent(new CustomEvent('dropdown-open'));
  }

  close() {
    this.isOpen = false;
    const trigger = this.shadowRoot.querySelector('.dropdown-trigger');
    const menu = this.shadowRoot.querySelector('.dropdown-menu');
    const searchInput = this.shadowRoot.querySelector('.search-input');

    trigger.classList.remove('open');
    trigger.setAttribute('aria-expanded', 'false');
    menu.classList.remove('open');

    if (searchInput) {
      searchInput.value = '';
      this.filterOptions('');
    }

    this.dispatchEvent(new CustomEvent('dropdown-close'));
  }

  selectOption(optionElement) {
    const value = optionElement.dataset.value;
    const text = optionElement.querySelector('span').textContent;
    const option = this.options.find(opt => opt.value === value);

    if (this.multiple) {
      option.selected = !option.selected;
      optionElement.classList.toggle('selected');
      const checkbox = optionElement.querySelector('.checkbox');
      if (checkbox) {
        checkbox.checked = option.selected;
      }
      
      this.updateMultipleSelection();
    } else {
      // Clear previous selection
      this.options.forEach(opt => opt.selected = false);
      this.shadowRoot.querySelectorAll('.dropdown-option').forEach(el => {
        el.classList.remove('selected');
        el.setAttribute('aria-selected', 'false');
      });

      // Set new selection
      option.selected = true;
      optionElement.classList.add('selected');
      optionElement.setAttribute('aria-selected', 'true');
      
      this.selectedValue = value;
      this.selectedText = text;
      
      const triggerSpan = this.shadowRoot.querySelector('.dropdown-trigger span');
      triggerSpan.textContent = text;
      triggerSpan.classList.remove('placeholder');
      
      this.close();
    }

    this.dispatchEvent(new CustomEvent('change', {
      detail: {
        value: this.multiple ? this.getSelectedValues() : value,
        text: this.multiple ? this.getSelectedTexts() : text
      }
    }));
  }

  deselectOption(value) {
    const option = this.options.find(opt => opt.value === value);
    if (option) {
      option.selected = false;
      const optionElement = this.shadowRoot.querySelector(`[data-value="${value}"]`);
      if (optionElement) {
        optionElement.classList.remove('selected');
        const checkbox = optionElement.querySelector('.checkbox');
        if (checkbox) {
          checkbox.checked = false;
        }
      }
      this.updateMultipleSelection();
      
      this.dispatchEvent(new CustomEvent('change', {
        detail: {
          value: this.getSelectedValues(),
          text: this.getSelectedTexts()
        }
      }));
    }
  }

  updateMultipleSelection() {
    const tagsContainer = this.shadowRoot.querySelector('.selected-tags');
    const triggerSpan = this.shadowRoot.querySelector('.dropdown-trigger span');
    
    const selectedOptions = this.options.filter(opt => opt.selected);
    
    if (selectedOptions.length === 0) {
      tagsContainer.innerHTML = '';
      triggerSpan.textContent = this.placeholder;
      triggerSpan.classList.add('placeholder');
    } else {
      tagsContainer.innerHTML = selectedOptions.map(option => `
        <span class="selected-tag" data-value="${option.value}">
          ${option.text}
          <span class="tag-remove">Ã—</span>
        </span>
      `).join('');
      
      triggerSpan.textContent = `${selectedOptions.length} selected`;
      triggerSpan.classList.remove('placeholder');
    }
  }

  filterOptions(searchTerm) {
    const options = this.shadowRoot.querySelectorAll('.dropdown-option');
    const term = searchTerm.toLowerCase();

    options.forEach(option => {
      const text = option.querySelector('span').textContent.toLowerCase();
      if (text.includes(term)) {
        option.classList.remove('hidden');
      } else {
        option.classList.add('hidden');
      }
    });
  }

  focusNextOption() {
    const options = Array.from(this.shadowRoot.querySelectorAll('.dropdown-option:not(.hidden)'));
    const currentIndex = options.findIndex(opt => opt === document.activeElement);
    const nextIndex = currentIndex < options.length - 1 ? currentIndex + 1 : 0;
    options[nextIndex]?.focus();
  }

  focusPreviousOption() {
    const options = Array.from(this.shadowRoot.querySelectorAll('.dropdown-option:not(.hidden)'));
    const currentIndex = options.findIndex(opt => opt === document.activeElement);
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : options.length - 1;
    options[prevIndex]?.focus();
  }

  getSelectedValues() {
    return this.options.filter(opt => opt.selected).map(opt => opt.value);
  }

  getSelectedTexts() {
    return this.options.filter(opt => opt.selected).map(opt => opt.text);
  }

  // Public API methods
  setValue(value) {
    if (this.multiple) {
      const values = Array.isArray(value) ? value : [value];
      this.options.forEach(option => {
        option.selected = values.includes(option.value);
      });
      this.renderOptions();
      this.updateMultipleSelection();
    } else {
      const option = this.options.find(opt => opt.value === value);
      if (option) {
        this.options.forEach(opt => opt.selected = false);
        option.selected = true;
        this.selectedValue = value;
        this.selectedText = option.text;
        
        const triggerSpan = this.shadowRoot.querySelector('.dropdown-trigger span');
        triggerSpan.textContent = option.text;
        triggerSpan.classList.remove('placeholder');
        
        this.renderOptions();
      }
    }
  }

  getValue() {
    return this.multiple ? this.getSelectedValues() : this.selectedValue;
  }

  reset() {
    this.options.forEach(opt => opt.selected = false);
    this.selectedValue = '';
    this.selectedText = '';
    
    const triggerSpan = this.shadowRoot.querySelector('.dropdown-trigger span');
    triggerSpan.textContent = this.placeholder;
    triggerSpan.classList.add('placeholder');
    
    if (this.multiple) {
      this.updateMultipleSelection();
    }
    
    this.renderOptions();
  }
}

// Register the custom element
customElements.define('dropdown-menu', DropdownMenu);
