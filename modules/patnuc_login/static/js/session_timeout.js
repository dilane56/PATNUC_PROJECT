odoo.define('patnuc_login.session_timeout', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');  // Charge le module de session d'Odoo
    var _t = core._t;

    // Durée avant expiration (5 minutes)
    var sessionTimeout = 300000; // 300000 ms = 5 minutes
    var UserErrorTimeout = sessionTimeout - 60000; // Avertir 1 minute avant

    // Variables pour les timers
    var UserErrorTimer, expirationTimer;

    // Fonction pour avertir l'utilisateur avant l'expiration
    function warnSessionExpiration() {
        alert(_t("Votre session va expirer dans 1 minute en raison d'une inactivité."));
    }

    // Fonction pour rediriger l'utilisateur après expiration
    function redirectToLogout() {
        // Vérifiez si l'utilisateur est connecté avant de rediriger
        if (session.is_authenticated) {
            alert(_t("Votre session a expiré. Vous allez être redirigé."));
            window.location.href = '/web/session/logout';  // Redirige vers la page de déconnexion
        }
    }

    // Initialiser les timers
    function initTimers() {
        UserErrorTimer = setTimeout(warnSessionExpiration, UserErrorTimeout);
        expirationTimer = setTimeout(redirectToLogout, sessionTimeout);
    }

    // Vérification de l'état de la session chaque minute
    function checkSessionStatus() {
        fetch('/web/session/check', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(function (data) {
            if (data.expired) {
                redirectToLogout();  // Déconnexion si la session est expirée
            }
        })
        .catch(function (error) {
            console.error("Erreur lors de la vérification de la session:", error);
        });
    }

    // Vérifier l'état de la session toutes les minutes
    setInterval(checkSessionStatus, 60000); // Vérifier chaque minute

    // Gestion de l'activité de l'utilisateur
    function resetActivityTimeout() {
        clearTimeout(UserErrorTimer);
        clearTimeout(expirationTimer);
        initTimers(); // Réinitialiser les timers
    }

    // Écouter les événements de mouvement de souris et de touches
    document.addEventListener('mousemove', resetActivityTimeout);
    document.addEventListener('keydown', resetActivityTimeout);
    
    // Initialiser le timer au chargement
    initTimers();
});