import { useEffect } from "react";
import * as d3 from "d3";

export default function LangDistributionChart({ data, id = "language-pie-chart" }) {
  useEffect(() => {
    // Exit early if no data
    if (!data || data.length === 0) return;

    // === Preprocess Data 
    // Calculate total count of all languages
    const total = data.reduce((sum, d) => sum + d.count, 0);

    // Group languages with under 1% =>"Others"
    const processedData = [];
    let othersCount = 0;

    data.forEach(d => {
      const pct = (d.count / total) * 100;
      if (pct < 1) {
        othersCount += d.count;
      } else {
        processedData.push(d);
      }
    });

    if (othersCount > 0) {
      processedData.push({ language: "Others", count: othersCount });
    }

    // ===  Define Chart Dimensions 
    const width = 400;
    const height = 400;
    const radius = Math.min(width, height) / 2;
    const svgId = `#${id}`;

    // Clear any existing SVG content before redrawing
    d3.select(svgId).selectAll("*").remove();

    // === Create SVG Canvas 
    const svg = d3
      .select(svgId)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    // === Define Color Scale 
    // Uses D3’s default categorical color palette
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // === Create Pie and Arc Generators 
    const pie = d3.pie().value(d => d.count);
    const data_ready = pie(processedData);

    const arc = d3.arc().innerRadius(0).outerRadius(radius);

    // === Draw Pie Segments 
    svg
      .selectAll("path")
      .data(data_ready)
      .join("path")
      .attr("d", arc)
      .attr("fill", d => color(d.data.language))
      .attr("stroke", "white")
      .style("stroke-width", "2px");

    // ===  Add Labels to Each Slice 
    svg
      .selectAll("text")
      .data(data_ready)
      .join("text")
      .text(
        d => `${d.data.language} (${((d.data.count / total) * 100).toFixed(1)}%)`
      )
      .attr("transform", d => `translate(${arc.centroid(d)})`)
      .style("text-anchor", "middle")
      .style("font-size", 12);
  }, [data, id]);

  // Render the SVG container
  return <svg id={id}></svg>;
}
