import  { useRef, useEffect } from "react";
import * as d3 from "d3";

export default function ConfidencePieChart({ confidence = 0.5, result = "Safe" }) {
  const ref = useRef();

  useEffect(() => {
    // == Prepare SVG container and remove previous drawings
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    // === Define chart size and layout
    const width = 260;
    const height = 280; // slightly taller to fit bottom label
    const radius = Math.min(width, height - 20) / 2;
    const centerX = width / 2;
    const centerY = height / 2 - 10;

    // ==Create chart group element
    const chart = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${centerX}, ${centerY})`);

    // == Set up data and color mapping
    // Automatically include the opposite result with the complementary confidence value
    const oppositeResult = result === "Vulnerable" ? "Safe" : "Vulnerable";
    const data = [
      { label: result, value: confidence },
      { label: oppositeResult, value: 1 - confidence },
    ];

    const color = d3
      .scaleOrdinal()
      .domain(["Vulnerable", "Safe"])
      .range(["#e74c3c", "#2ecc71"]);

    // == Create pie layout and arc generators
    const pie = d3.pie().value((d) => d.value);
    const arc = d3.arc().innerRadius(55).outerRadius(radius - 5);
    const arcHover = d3.arc().innerRadius(50).outerRadius(radius + 6);

    // == Define tooltip style and container
    const tooltip = d3
      .select("body")
      .selectAll(".confidence-tooltip")
      .data([0])
      .join("div")
      .attr("class", "confidence-tooltip")
      .style("position", "absolute")
      .style("background", "rgba(30, 30, 30, 0.9)")
      .style("color", "#fff")
      .style("padding", "6px 10px")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    // == Draw pie chart slices and handle interactivity
    chart
      .selectAll("path")
      .data(pie(data))
      .join("path")
      .attr("d", arc)
      .attr("fill", (d) => color(d.data.label))
      .attr("stroke", "#222")
      .style("stroke-width", "2px")
      .style("cursor", "pointer")
      .on("mouseover", function (event, d) {
        // Expand hovered slice
        d3.select(this)
          .transition()
          .duration(150)
          .attr("d", arcHover)
          .style("filter", "brightness(1.2)");

        // Show tooltip near cursor
        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${d.data.label}</strong><br>${(d.data.value * 100).toFixed(1)}%`
          )
          .style("left", event.pageX + 12 + "px")
          .style("top", event.pageY - 28 + "px");
      })
      .on("mousemove", (event, d) => {
        // Recalculate tooltip position to keep it within the viewport
        const tooltipWidth = 100;
        const tooltipHeight = 50;
        const padding = 12;

        let x = event.pageX + padding;
        let y = event.pageY - tooltipHeight - padding;

        if (x + tooltipWidth > window.innerWidth) {
          x = event.pageX - tooltipWidth - padding;
        }
        if (y < 0) {
          y = event.pageY + padding;
        }

        tooltip
          .style("opacity", 1)
          .html(
            `<strong>${d.data.label}</strong><br>${(d.data.value * 100).toFixed(1)}%`
          )
          .style("left", `${x}px`)
          .style("top", `${y}px`);
      })
      .on("mouseout", function () {
        // Reset slice and hide tooltip
        d3.select(this)
          .transition()
          .duration(150)
          .attr("d", arc)
          .style("filter", "brightness(1)");
        tooltip.style("opacity", 0);
      });

    // == Add center percentage label
    chart
      .append("text")
      .attr("text-anchor", "middle")
      .attr("fill", "#fff")
      .style("font-size", "20px")
      .style("font-weight", "bold")
      .text(`${(confidence * 100).toFixed(1)}%`);

    // == Add center result label below percentage
    chart
      .append("text")
      .attr("text-anchor", "middle")
      .attr("fill", result === "Vulnerable" ? "#ff6b6b" : "#66ff99")
      .attr("y", 22)
      .style("font-size", "14px")
      .style("font-weight", "600")
      .text(result);

    // == Add bottom axis label
    chart
      .append("text")
      .attr("text-anchor", "middle")
      .attr("fill", "#ccc")
      .attr("y", radius + 35)
      .style("font-size", "15px")
      .style("font-weight", "700")
      .text("Confidence Ratio");
  }, [confidence, result]);

  // == Return the SVG container
  return (
    <svg
      ref={ref}
      style={{
        width: "100%",
        height: "auto",
        display: "block",
        overflow: "visible",
      }}
    />
  );
}
