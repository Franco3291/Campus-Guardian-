document.addEventListener('DOMContentLoaded', () => {
  const sosButton = document.getElementById('sosBtn');

  if (sosButton) {
    sosButton.addEventListener('click', async () => {
      try {
        const response = await fetch('/sos', { method: 'POST' });
        const result = await response.json();
        alert(`${result.status}: ${result.incident.title}`);
      } catch (error) {
        alert('SOS alert failed. Please try again.');
      }
    });
  }
});
