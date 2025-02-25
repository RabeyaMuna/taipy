import React from "react";
import useStore from "../../store";

const TaipyElementEditor = () => {
    const element = useStore((state) => state.selectedElement);
    return element ? <div>{element.id}</div> : <div>No Element Selected</div>;
};

export default TaipyElementEditor;
