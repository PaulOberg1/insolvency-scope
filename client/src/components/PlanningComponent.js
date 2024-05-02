import polyline from "polyline";
import {useState, useEffect} from "react";


const PlanningComponent = ({setMapHTML,startPos,setStartPos,endPos,setEndPos,latitude,setLatitude,longitude,setLongitude}) => {

    const [instructions,setInstructions]=useState(null)

    const displayRoute = async () => {
        console.log("called display route via start and end pos " + startPos + endPos);
        //const sp = startPos.split(",").map(val => parseFloat(val));
        //const ep = endPos.split(",").map(val => parseFloat(val));
        //console.log("sp = " + sp + " and ep = " + ep);
        const c = "52.3793,1.5615";
        const sp = startPos.split(",").reverse().join();
        const ep = endPos.split(",").reverse().join();
        console.log(sp)
        console.log("coords = 52.3793,1.5615\ncoords = " + c + `\ncoords = ${c}`);
        console.log("startPos = " + startPos + " and endPos = " + endPos);
        const apiUrl = `https://router.project-osrm.org/route/v1/driving/${sp};${ep}?alternatives=1&steps=true`;
        try{
            const response = await fetch(apiUrl);
            if (response.ok) {
                console.log("route data from apiurl fetched");
            }
            else {
                console.log("error fetching apirurl route data,"+response);
            }
            const data = await response.json();
            const routeGeometry = data.routes[0].geometry;
            const steps = data.routes[0].legs[0].steps;
            const decodedCoordinates = polyline.decode(routeGeometry);
            const arr = [];
            steps.forEach(element => {
                if ("type" in element.maneuver) {
                    if ("exit" in element.maneuver) {
                        arr.push([element.name + " - " + element.maneuver.type + " at a " + element.maneuver.modifier + " at exit " + element.maneuver.exit,element.geometry,element.maneuver.location])
                    }
                    else {
                        arr.push([element.name + " - " + element.maneuver.type + element.maneuver.modifier,element.geometry,element.maneuver.location])
                    }
                    
                }
            });
            setInstructions(arr);
            
            const response2 = await fetch("/modifyMap",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({
                    "data":decodedCoordinates,
                    "instructions":instructions,
                    "centreLat":latitude,
                    "centreLong":longitude,
                    "startPos":startPos,
                    "endPos":endPos
                })
            });
            if (response2.ok) {
                const data = await response2.text();
                setMapHTML(data);
            }
            else {
                console.log("error sending/receiving route data to/from backend");
            }
        }
        catch(e) {
            console.log("error getting route data from apiurl");
        }
        
    }

    const highlightRoute = (geometry,location) => {
        fetch("/highlight", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                "geometry":geometry,
                "location":location
            })
        })
        .then(response => response.text())
        .then(result => {setMapHTML(result.data)})
        .catch(error => console.error("error highlighting route: ",error.message));
    }
    const clearHighlights = () => {
        fetch("/clearHighlights")
        .then(response => response.text())
        .then(result => {setMapHTML(result)})
        .catch(error => {console.error("error clearing highlights : ",error.message)});
    }


    return (
        <div>
            {instructions &&
            <div>
                <p>Instructions!</p>
                {instructions.map(([instruction,pline,loc],index) => {
                    return (
                        <div key={index}>
                        <div style={{backgroundColor:"blue"}} onMouseEnter={() => {highlightRoute(pline,loc)}} onMouseLeave={clearHighlights}>
                        <p>{instruction}</p>
                        </div><br/>
                        </div>
                    )})}
                
            </div>
            }
            
            <label>Enter starting position</label>
            <input type="text" value={startPos} onChange={(event) => setStartPos(event.target.value)}/>
            <br />
            <label>Enter destination</label>
            <input type="text" value={endPos} onChange={(event) => setEndPos(event.target.value)}/>
            <button onClick={displayRoute}>Get directions</button>
        </div>
    )
};

export default PlanningComponent;