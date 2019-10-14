
// The first step is obtain all the latitude and longitude from the HTML
// The below is a simple jQuery selector
// $("#coordinates").each(function () {
// $(document).ready(function(){
var longitude = $("#longitude").text().trim();
var latitude = $("#latitude").text().trim();
var description = $("#description").text().trim();
console.log(description);

mapboxgl.accessToken = 'pk.eyJ1IjoieHVlamluaHVhbmciLCJhIjoiY2psdDA1dDV5MDJzeTN2bGRxcGNodHY5YSJ9.Hx5ukpvIPwuE4kDn2JQW4Q';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    zoom: 13,
    center: [longitude, latitude]
});

// var geojson = {
//   type: 'FeatureCollection',
//   features: [{
//     type: 'Feature',
//     geometry: {
//       type: 'Point',
//       coordinates: [longitude, latitude]
//     },
//     properties: {
//       description: description,
//       // marker: {color: 'red'}
//     }
//   }]
// }
// create the popup
var popup = new mapboxgl.Popup({ offset: 25 })
.setText(description);

new mapboxgl.Marker()
.setLngLat([longitude, latitude])
.setPopup(popup) // sets a popup on this marker
.addTo(map);

var geocoder = new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    marker: {
    color: 'orange'
    },
    mapboxgl: mapboxgl
});

map.addControl(geocoder);

map.addControl(new MapboxDirections({
    accessToken: mapboxgl.accessToken,
}), 'top-left');

map.addControl(new mapboxgl.GeolocateControl({
    positionOptions: {
    enableHighAccuracy: true
    },
    trackUserLocation: true
}));

map.addControl(new mapboxgl.NavigationControl());










