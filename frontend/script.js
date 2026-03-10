const API = "http://127.0.0.1:8000"

async function requestRide(){

await fetch(`${API}/rides/request`,{

method:"POST",
headers:{"Content-Type":"application/json"},

body:JSON.stringify({
rider_id:1,
pickup_lat:17.3851,
pickup_lng:78.4867,
drop_lat:17.3951,
drop_lng:78.4967
})

})

alert("Ride Requested")

}

async function updateLocation(){

await fetch(`${API}/drivers/location`,{

method:"POST",
headers:{"Content-Type":"application/json"},

body:JSON.stringify({
driver_id:201,
lat:17.3851,
lng:78.4867
})

})

alert("Location Updated")

}

async function acceptRide(){

let id=document.getElementById("ride_id").value

await fetch(`${API}/rides/${id}/accept?driver_id=201`,{
method:"POST"
})

alert("Ride Accepted")

}

async function startRide(){

let id=document.getElementById("ride_id").value

await fetch(`${API}/rides/${id}/start`,{
method:"POST"
})

alert("Ride Started")

}

async function completeRide(){

let id=document.getElementById("ride_id").value

await fetch(`${API}/rides/${id}/complete`,{
method:"POST"
})

alert("Ride Completed")

}

async function payRide(){

let id=document.getElementById("ride_id").value

await fetch(`${API}/rides/${id}/create-payment`,{
method:"POST"
})

alert("Payment Created")

}