// Moved from src/KnowledgePage.js
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from "d3";
import { Container, Typography, Box, Card, CardContent } from '@mui/material';
import { useAuth } from '../context/AuthContext';

export default function KnowledgePage() {
    const { user } = useAuth();

    return (
        <Container>
            <Typography variant="h3" component="h1" gutterBottom>
                Knowledge Base
            </Typography>

            <Box sx={{ mt: 2 }}>
                <Card>
                    <CardContent>
                        {user ? (
                            <Typography variant="body1">
                                Welcome {user.name || user.email}! Explore articles and resources here.
                            </Typography>
                        ) : (
                            <Typography variant="body1">
                                This is the knowledge base. Sign in to see personalised recommendations.
                            </Typography>
                        )}
                    </CardContent>
                </Card>
            </Box>

            {/* Chart Section */}
            <Box sx={{ mt: 4 }}>
                <Card>
                    <CardContent>
                        <Visualization />
                    </CardContent>
                </Card>
            </Box>
        </Container>
    );
}

const Visualization = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/visualization")
        .then(res => res.json())
        .then(data => {
            setChartData(data);
        })
        .catch(err => console.error("Failed to fetch visualization data:", err));
  }, []);

  if (!chartData || chartData === null) return <p>Loading charts...</p>;

  return (
    <div>
        <h1 style={{ textAlign: "center" }}>Code Vulnerabilities Dashboard</h1>

        <h2>Language Distribution</h2>
        <LangDistributionChart data={chartData.language_distribution} />

        <h2>Token Frequency: Safe vs Vulnerable</h2>
        <TokenFrequencyChart data={chartData.token_frequency} />

    </div>
  );
};

const TokenFrequencyChart = ({ data }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0) return;

    const margin = { top: 30, right: 30, bottom: 120, left: 60 };
    const width = 900 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    d3.select(chartRef.current).selectAll("*").remove();

    const svg = d3
      .select(chartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x0 = d3.scaleBand()
      .domain(data.map(d => d.token))
      .range([0, width])
      .padding(0.2);

    const x1 = d3.scaleBand()
      .domain(["safe", "vulnerable"])
      .range([0, x0.bandwidth()])
      .padding(0.05);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.safe, d.vulnerable))])
      .nice()
      .range([height, 0]);

    const color = d3.scaleOrdinal()
      .domain(["safe", "vulnerable"])
      .range(["#4CAF50", "#D32F2F"]);

    svg.append("g")
      .selectAll("g")
      .data(data)
      .enter()
      .append("g")
      .attr("transform", d => `translate(${x0(d.token)},0)`)
      .selectAll("rect")
      .data(d => [
        { key: "safe", value: d.safe },
        { key: "vulnerable", value: d.vulnerable }
      ])
      .enter()
      .append("rect")
      .attr("x", d => x1(d.key))
      .attr("y", d => y(d.value))
      .attr("width", x1.bandwidth())
      .attr("height", d => height - y(d.value))
      .attr("fill", d => color(d.key));

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x0))
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end")
      .style("font-size", "11px");

    svg.append("g").call(d3.axisLeft(y));

    const legend = svg.append("g").attr("transform", `translate(${width - 120},0)`);
    ["safe", "vulnerable"].forEach((k, i) => {
      legend.append("rect")
        .attr("x", 0)
        .attr("y", i * 22)
        .attr("width", 18)
        .attr("height", 18)
        .attr("fill", color(k));

      legend.append("text")
        .attr("x", 25)
        .attr("y", i * 22 + 14)
        .text(k.charAt(0).toUpperCase() + k.slice(1));
    });
  }, [data]);

  return <div ref={chartRef}></div>;
};

const LangDistributionChart = ({ data, id = "language-pie-chart" }) => {
  useEffect(() => {
    if (!data || data.length === 0) return;

    const total = data.reduce((sum, d) => sum + d.count, 0);

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

    const width = 400;
    const height = 400;
    const radius = Math.min(width, height) / 2;
    const svgId = `#${id}`;

    d3.select(svgId).selectAll("*").remove();

    const svg = d3
      .select(svgId)
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const pie = d3.pie().value(d => d.count);
    const data_ready = pie(processedData);

    const arc = d3.arc().innerRadius(0).outerRadius(radius);

    svg.selectAll("path")
      .data(data_ready)
      .join("path")
      .attr("d", arc)
      .attr("fill", d => color(d.data.language))
      .attr("stroke", "white")
      .style("stroke-width", "2px");

    svg.selectAll("text")
      .data(data_ready)
      .join("text")
      .text(d => `${d.data.language} (${((d.data.count / total) * 100).toFixed(1)}%)`)
      .attr("transform", d => `translate(${arc.centroid(d)})`)
      .style("text-anchor", "middle")
      .style("font-size", 12);
  }, [data, id]);

  return <svg id={id}></svg>;
};
