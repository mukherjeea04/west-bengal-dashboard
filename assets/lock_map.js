(function () {

    function lockMapTouch() {

        const mapContainer = document.getElementById("district-map");

        if (!mapContainer) {
            return;
        }

        if (mapContainer.dataset.touchLocked === "true") {
            return;
        }

        mapContainer.dataset.touchLocked = "true";

        const blockTouch = function (event) {
            event.preventDefault();
        };

        mapContainer.addEventListener(
            "touchstart",
            blockTouch,
            { passive: false }
        );

        mapContainer.addEventListener(
            "touchmove",
            blockTouch,
            { passive: false }
        );

        mapContainer.addEventListener(
            "touchend",
            blockTouch,
            { passive: false }
        );
    }


    // Dash/Plotly may create the map after the page loads,
    // so check repeatedly until it exists.

    const observer = new MutationObserver(function () {
        lockMapTouch();
    });

    observer.observe(
        document.body,
        {
            childList: true,
            subtree: true
        }
    );


    // Initial check
    lockMapTouch();

})();