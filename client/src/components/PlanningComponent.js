import {useState} from "react";


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
        const response2 = await fetch("/modifyMap",{
            method:"POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                "startPos":sp,
                "endPos":ep
            })
        });
        if (response2.ok) {
            const data = await response2.json();
            const mapHTML = data.mapHTML;
            const instructions = data.instructions;
            setMapHTML(mapHTML);
            setInstructions(instructions)
            console.log(instructions);
        }
        else
            console.log("error sending/receiving route data to/from backend");
        return 0;
    }

    const highlightRoute = (geometry,location) => {
        return 0;
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
        return 0;
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
                {instructions.map((x,i) => {
                    return (
                    <div key={i}>
                        <p>{x}</p>
                    </div>
                    );
                })}
                
                
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