let storedUserSettings;

async function fetchUserSettings() {
  try {
    const response = await fetch("/api/users/@me");

    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }

    if (!response.ok) {
      const errorText = await response.text();
      alertManager.newAlert(errorText, "error", 5000, "Settings Error");
      return;
    }

    const body = await response.json();
    storedUserSettings = body;
    if (body && body.username) {
      document.getElementById('username').value = body.username;
    }
  } catch (error) {
    alertManager.newAlert(
      "Failed to fetch user settings. Please try again.",
      "error",
      5000,
      "Settings Error"
    );
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  try {
    const response = await fetch("/api/users/settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      alertManager.newAlert(errorText, "error", 5000, "Settings Update Error");
      return;
    }

    // Show success message and reload page
    window.location.reload();
  } catch (error) {
    alertManager.newAlert(
      "Failed to update settings. Please try again.",
      "error",
      5000,
      "Settings Error"
    );
  }
}

const dialog = document.getElementById("twoFactorDialog");
const enable2faBtn = document.getElementById("enable2fa");
const closeDialogBtn = document.getElementById("closeDialog");
const doneButton = document.getElementById("doneButton");
const qrCodeImg = document.getElementById("qrCode");
const secretCodeElement = document.getElementById("secretCode");
const form = document.querySelector("form");

// Show dialog
enable2faBtn.addEventListener("click", async () => {
  const response = await fetch("/api/totp/enable", { method: "POST" });
  const totpBody = await response.json();

  if (!response.ok || !totpBody.secret) {
    alertManager.newAlert(
      "Failed to enable 2FA. Either request failed, or no secret was returned",
      "error",
      10000,
      "2FA Enable Failed"
    );
    return;
  }

  if (!storedUserSettings || !storedUserSettings.username) {
    alertManager.newAlert(
      "Could not find username in user settings. Is your /api/users/@me endpoint working?",
      "error",
      10000,
      "2FA Enable Failed"
    );
    return;
  }
  const secret = totpBody.secret;

  // Generate otpauth URL for QR code
  const otpauthUrl = `otpauth://totp/312site:${encodeURIComponent(`${storedUserSettings.username}@312site.com`)}?secret=${secret}&issuer=YourApp`;

  // Set QR code image
  qrCodeImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
    otpauthUrl
  )}`;

  // Display secret code
  secretCodeElement.textContent = secret;

  // Show dialog
  dialog.classList.remove("hidden");
});

// Close dialog
function closeDialog() {
  dialog.classList.add("hidden");
}

closeDialogBtn.addEventListener("click", closeDialog);
doneButton.addEventListener("click", closeDialog);


fetchUserSettings();

// document.getElementById("avatar").addEventListener("change", function (event) {
//   const file = event.target.files[0];
//   if (file) {
//     const reader = new FileReader();
//     reader.onload = function (e) {
//       document.getElementById("avatar-preview").src = e.target.result;
//     };
//     reader.readAsDataURL(file);
//   }
// });
