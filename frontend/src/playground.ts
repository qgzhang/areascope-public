// const productName: string = "AreaScope";

// let zoom: number = 10;

const suburbs: string[] = [
    "Kenmore",
    "Indooroopilly",
    "Moggill",
];

interface AreaSummary {
    name: string;
    addressCount: number;
    areaKm2: number;
}

const area: AreaSummary = {
    name: "Kenmore",
    addressCount: 4200,
    areaKm2: 6.8,
};

function describeArea(area: AreaSummary): string {
    return `${area.name}: ${area.addressCount} addresses`;
}

console.log(describeArea(area));


console.log(suburbs);
console.log(suburbs[0]);
console.log(suburbs[1]);

console.log(suburbs.length);

suburbs.forEach((suburb) => {
  console.log(suburb);
});

let selectedSuburb: string | null = null;
console.log(selectedSuburb);

selectedSuburb = "Kenmore";

console.log(selectedSuburb);


const upperCaseSuburbs = suburbs.map((suburb) => {
  return suburb.toUpperCase();
});

console.log(upperCaseSuburbs);


//
//
//
// import { useState } from 'react';
//
// function Counter() {
//     const [count, setCount] = useState(0);
//
//     return (
//         <div>
//             <p>Count: {count}</p>
//
//             <button onClick={() => setCount(count + 1)}>
//                 Increase
//             </button>
//         </div>
//     );
// }
//
//
// const [mode, setMode] =
//     useState<'polygon' | 'suburb'>('suburb');
//
//
// <button onClick={() => setMode('suburb')}>
//     Suburb
// </button>
//
// <button onClick={() => setMode('polygon')}>
//     Polygon
// </button>
//
// <p>Current mode: {mode}</p>