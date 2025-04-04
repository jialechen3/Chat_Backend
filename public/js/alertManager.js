class AlertManager {
  constructor() {
    const container = document.querySelector("#alert-container");
    if (!container) {
      throw new Error(
        "Alert container element with id 'alert-container' not found!"
      );
    }
    this.container = container;
    this.alerts = new Map();
  }

  newAlert(message, type = "info", duration = 5000, title = "Alert") {
    const id = crypto.randomUUID();
    const alertElement = this.createAlertElement(id, message, type, title);

    this.container.append(alertElement);
    this.alerts.set(id, alertElement);

    if (duration > 0) {
      setTimeout(() => this.removeAlert(id), duration);
    }

    return id;
  }

  removeAlert(id) {
    const alert = this.alerts.get(id);
    if (alert) {
      alert.classList.add("opacity-0"); // Hide to fade out
      setTimeout(() => {
        alert.remove();
        this.alerts.delete(id);
      }, 300);
    }
  }

  clearAlerts() {
    this.alerts.forEach((_, id) => this.removeAlert(id));
  }

  getIconForType(type) {
    switch (type) {
      case "success":
        return "check-circle";
      case "error":
        return "alert-circle";
      case "warning":
        return "alert-triangle";
      default:
        return "info";
    }
  }

  createAlertElement(id, message, type = "info", title = "Alert") {
    // Allows for different colors for different alert types, targets h3 headers and svgs for icons aswell
    const colorClasses = {
      success: "border-green-500 [&_svg]:text-green-500 [&_h3]:text-green-500",
      error: "border-red-500 [&_svg]:text-red-500 [&_h3]:text-red-500",
      info: "border-blue-500 [&_svg]:text-blue-500 [&_h3]:text-blue-500",
      warning:
        "border-yellow-500 [&_svg]:text-yellow-500 [&_h3]:text-yellow-500",
    };

    const alert = document.createElement("div");
    // start hidden to allow fade in
    alert.className = `opacity-0 transition-all duration-300 transform translate-y-[-1rem] w-full p-4 bg-primary border-2 rounded-lg shadow-lg flex flex-col gap-2 ${colorClasses[type]} `;
    alert.id = id;

    alert.innerHTML = `
    <div class="flex justify-between items-center mb-2">
        <div class="flex items-center gap-3">
            <i data-lucide="${this.getIconForType(type)}" class="w-6 h-6"></i>
            <h3 class="font-semibold text-xl">${title}</h3>
        </div>
        <button class="text-gray-400 hover:text-white" onclick="alertManager.removeAlert('${id}')">
            <i data-lucide="x" class="w-5 h-5"></i>
        </button>
        </div>
    <p class="text-white leading-relaxed">${message}</p>
    `;

    // Let element render first, then remove opacity
    setTimeout(() => {
      alert.classList.remove("opacity-0");
      alert.classList.remove("translate-y-[-1rem]");
      lucide.createIcons({
        elements: alert.querySelectorAll("[data-lucide]"),
      });
    }, 100);

    return alert;
  }
}

// Global variable for alertManager
const alertManager = new AlertManager();
