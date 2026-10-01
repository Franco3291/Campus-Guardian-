document.addEventListener('DOMContentLoaded', () => {
  const sosButton = document.getElementById('sosBtn');
  const useLocationBtn = document.getElementById('useLocationBtn');
  const locationInput = document.getElementById('locationInput');
  const latInput = document.getElementById('latInput');
  const lngInput = document.getElementById('lngInput');
  const locationStatus = document.getElementById('locationStatus');
  const reportMapStatus = document.getElementById('reportMapStatus');
  const locationMapLink = document.getElementById('locationMapLink');
  let reportMap;
  let reportMarker;

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
    if (reportMarker && reportMap) {
      const position = { lat, lng };
      reportMarker.setPosition(position);
      reportMap.setCenter(position);
      reportMap.setZoom(17);
    }
    if (locationMapLink) {
      locationMapLink.href = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
      locationMapLink.hidden = false;
    }
    if (reportMapStatus) {
      reportMapStatus.textContent = 'Report location preview updated.';
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

      useLocationBtn.disabled = true;
      useLocationBtn.textContent = 'Locating...';

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          const accuracy = position.coords.accuracy;
          const accuracyLabel = `${Math.round(accuracy)}m accuracy`;
          setCurrentLocation(lat, lng, accuracyLabel);
          useLocationBtn.disabled = false;
          useLocationBtn.textContent = 'Update my location';
        },
        () => {
          if (locationStatus) {
            locationStatus.textContent = 'Location access was denied. Please allow location access to auto-fill the report.';
          }
          useLocationBtn.disabled = false;
          useLocationBtn.textContent = 'Use my location';
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
  const campusMapNode = document.getElementById('campusMap');
  const reportMapNode = document.getElementById('reportMap');
  const mapStatus = document.getElementById('dashboardMapStatus');
  const incidentDataNode = document.getElementById('incidentMapData');
  const campusCenter = { lat: 6.5244, lng: 3.3792 };
  let incidents = [];

  if (incidentDataNode) {
    try {
      incidents = JSON.parse(incidentDataNode.textContent);
    } catch (error) {
      if (mapStatus) mapStatus.textContent = 'Incident location data could not be loaded.';
    }
  }

  if (!googleMapsApiKey) {
    if (mapStatus) mapStatus.textContent = 'Set GOOGLE_MAPS_API_KEY to display interactive incident pins.';
    if (reportMapStatus) reportMapStatus.textContent = 'Set GOOGLE_MAPS_API_KEY to display the interactive location preview.';
  } else if (campusMapNode || reportMapNode) {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(googleMapsApiKey)}`;
    script.async = true;
    script.defer = true;
    script.onload = () => {
      const mapOptions = {
        center: campusCenter,
        zoom: 15,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
      };

      if (campusMapNode) {
        const campusMap = new google.maps.Map(campusMapNode, mapOptions);
        const bounds = new google.maps.LatLngBounds();
        let markerCount = 0;

        incidents.forEach((incident) => {
          const position = { lat: Number(incident.lat), lng: Number(incident.lng) };
          if (!Number.isFinite(position.lat) || !Number.isFinite(position.lng)) return;

          const marker = new google.maps.Marker({
            position,
            map: campusMap,
            title: `${incident.severity}: ${incident.title}`,
          });
          const info = document.createElement('div');
          const title = document.createElement('strong');
          title.textContent = incident.title;
          const details = document.createElement('p');
          details.textContent = `${incident.category} · ${incident.severity} · ${incident.status}`;
          info.append(title, details);
          const infoWindow = new google.maps.InfoWindow({ content: info });
          marker.addListener('click', () => infoWindow.open({ map: campusMap, anchor: marker }));
          bounds.extend(position);
          markerCount += 1;
        });

        if (markerCount > 1) campusMap.fitBounds(bounds);
        if (mapStatus) {
          mapStatus.textContent = markerCount
            ? `${markerCount} incident location${markerCount === 1 ? '' : 's'} shown.`
            : 'No incidents have GPS coordinates yet.';
        }
      }

      if (reportMapNode) {
        reportMap = new google.maps.Map(reportMapNode, { ...mapOptions, zoom: 15 });
        reportMarker = new google.maps.Marker({ map: reportMap, title: 'Reported incident location' });
        if (latInput && lngInput && latInput.value && lngInput.value) {
          const position = { lat: Number(latInput.value), lng: Number(lngInput.value) };
          reportMarker.setPosition(position);
          reportMap.setCenter(position);
        }
      }
    };
    script.onerror = () => {
      if (mapStatus) mapStatus.textContent = 'Google Maps could not load. Check the API key and Maps JavaScript API settings.';
      if (reportMapStatus) reportMapStatus.textContent = 'Google Maps could not load. Check the API key and Maps JavaScript API settings.';
    };
    document.head.appendChild(script);
  }
});
