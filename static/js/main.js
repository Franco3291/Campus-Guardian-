document.addEventListener('DOMContentLoaded', () => {
  const sosButton = document.getElementById('sosBtn');
  const useLocationBtn = document.getElementById('useLocationBtn');
  const locationInput = document.getElementById('locationInput');
  const latInput = document.getElementById('latInput');
  const lngInput = document.getElementById('lngInput');
  const locationStatus = document.getElementById('locationStatus');

  const setCurrentLocation = (lat, lng, accuracyLabel = '') => {
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;
    if (locationInput) {
      locationInput.value = `Current location (${lat.toFixed(5)}, ${lng.toFixed(5)})`;
    }
    if (locationStatus) {
      locationStatus.textContent = accuracyLabel
        ? `Location captured: ${lat.toFixed(5)}, ${lng.toFixed(5)} (${accuracyLabel})`
        : `Location captured: ${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    }
  };

  if (useLocationBtn) {
    useLocationBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        if (locationStatus) {
          locationStatus.textContent = 'Geolocation is not supported by this browser.';
        }
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const accuracy = position.coords.accuracy;
          const accuracyLabel = `${Math.round(accuracy)}m accuracy`;
          setCurrentLocation(lat, lng, accuracyLabel);
        },
        () => {
          if (locationStatus) {
            locationStatus.textContent = 'Location access was denied. Please allow location access to auto-fill the report.';
          }
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
      );
    });
  }

  if (sosButton) {
    sosButton.addEventListener('click', async () => {
      const formData = new FormData();
      if (latInput && latInput.value && lngInput && lngInput.value) {
        formData.append('lat', latInput.value);
        formData.append('lng', lngInput.value);
      }

      try {
        const response = await fetch('/sos', {
          method: 'POST',
          body: formData,
        });
        const result = await response.json();
        alert(`${result.status}: ${result.message}`);
      } catch (error) {
        alert('SOS alert failed. Please try again.');
      }
    });
  }

  const googleMapsApiKey = window.GOOGLE_MAPS_API_KEY || '';
  const mapNode = document.getElementById('campusMap');

  if (googleMapsApiKey && mapNode) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      const campusMap = new google.maps.Map(mapNode, {
        center: { lat: 6.5244, lng: 3.3792 },
        zoom: 15,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
      });

      new google.maps.Marker({
        position: { lat: 6.5244, lng: 3.3792 },
        map: campusMap,
        title: 'Campus Safety Center',
      });
    };
    document.head.appendChild(script);
  }
});
