import React from "react";

function Human() {
    const handleClick = () => {
      const userInput = window.prompt("Human input interruption: ", "Type response here...");
      if (userInput !== null) {
        console.log("User entered:", userInput);
      }
    };
  
    return (
      <div>
        <button onClick={handleClick}>Input</button>
      </div>
    );
  }
  
  export default Human;