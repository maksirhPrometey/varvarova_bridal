const form = document.querySelector('[data-checkout-form]');
if (form) {
  const citiesUrl = form.dataset.npCitiesUrl;
  const warehousesUrl = form.dataset.npWarehousesUrl;
  const cityInput = form.querySelector('[data-np-city]');
  const cityRef = form.querySelector('[name="np_city_ref"]');
  const warehouseSelect = form.querySelector('[data-np-warehouse]');
  const warehouseName = form.querySelector('[name="np_warehouse_name"]');
  const suggest = form.querySelector('[data-np-suggest]');

  function selectedShipping() {
    return form.querySelector('[name="shipping_method"]:checked')?.value || '';
  }

  function togglePanels() {
    const method = selectedShipping();
    form.querySelectorAll('[data-shipping-panel]').forEach((panel) => {
      const key = panel.dataset.shippingPanel;
      const on =
        (key === 'pickup_salon' && method === 'pickup_salon') ||
        (key === 'np_city' && (method === 'np_warehouse' || method === 'np_courier')) ||
        (key === 'np_warehouse' && method === 'np_warehouse') ||
        (key === 'np_courier' && method === 'np_courier');
      panel.hidden = !on;
    });
  }

  function hideSuggest() {
    if (suggest) {
      suggest.hidden = true;
      suggest.replaceChildren();
    }
  }

  async function loadCities(query) {
    if (!citiesUrl || !suggest) {
      return;
    }
    const response = await fetch(`${citiesUrl}?q=${encodeURIComponent(query)}`, {
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    suggest.replaceChildren();
    (data.results || []).forEach((city) => {
      const item = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = city.name;
      button.dataset.ref = city.ref;
      button.dataset.name = city.name;
      item.append(button);
      suggest.append(item);
    });
    suggest.hidden = !suggest.childElementCount;
  }

  async function loadWarehouses(cityRefValue) {
    if (!warehouseSelect || !warehousesUrl) {
      return;
    }
    warehouseSelect.replaceChildren();
    const empty = document.createElement('option');
    empty.value = '';
    empty.textContent = 'Оберіть відділення';
    warehouseSelect.append(empty);
    if (!cityRefValue) {
      return;
    }
    const response = await fetch(
      `${warehousesUrl}?city=${encodeURIComponent(cityRefValue)}`,
      { headers: { Accept: 'application/json' } },
    );
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    (data.results || []).forEach((row) => {
      const option = document.createElement('option');
      option.value = row.ref;
      option.textContent = row.name;
      warehouseSelect.append(option);
    });
  }

  function pickCity(ref, name) {
    if (cityInput) {
      cityInput.value = name;
    }
    if (cityRef) {
      cityRef.value = ref;
    }
    hideSuggest();
    if (warehouseName) {
      warehouseName.value = '';
    }
    loadWarehouses(ref);
  }

  form.querySelectorAll('[name="shipping_method"]').forEach((input) => {
    input.addEventListener('change', togglePanels);
  });

  if (cityInput) {
    let timer = 0;
    cityInput.addEventListener('input', () => {
      if (cityRef) {
        cityRef.value = '';
      }
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        loadCities(cityInput.value);
      }, 200);
    });
  }

  suggest?.addEventListener('click', (event) => {
    const button = event.target.closest('button');
    if (!button) {
      return;
    }
    pickCity(button.dataset.ref, button.dataset.name);
  });

  warehouseSelect?.addEventListener('change', () => {
    const option = warehouseSelect.selectedOptions[0];
    if (warehouseName) {
      warehouseName.value = option && option.value ? option.textContent : '';
    }
  });

  document.addEventListener('click', (event) => {
    if (suggest && !suggest.contains(event.target) && event.target !== cityInput) {
      hideSuggest();
    }
  });

  togglePanels();
  if (cityRef?.value) {
    loadWarehouses(cityRef.value);
  }
}
