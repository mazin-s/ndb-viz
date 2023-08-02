import Plot from "react-plotly.js";

interface Props {
    data: any;
    layout: any;
    className: any;
    style: any;
    useResizeHandler: any;
    onAfterPlot: any;
    setArePlotsLoading: any;
    dataObj: any;
}

export default function MyPlot({
    data,
    layout,
    className,
    style,
    useResizeHandler,
    onAfterPlot,
    setArePlotsLoading,
    dataObj,
}: Props) {
    return (
        <Plot
            data={dataObj["data"]}
            layout={dataObj["layout"]}
            className="w-full h-full"
            style={{ width: "100%", height: "100%" }}
            useResizeHandler
            onAfterPlot={() => setArePlotsLoading(false)}
        />
    )
}
