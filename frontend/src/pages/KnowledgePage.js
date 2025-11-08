import { useEffect, useState } from 'react';
import { Container, Typography, Box, Card, CardContent, Accordion,
  AccordionSummary,
  AccordionDetails,
  Link } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import LangDistributionChart from '../components/charts/LangDistributionChart';
import VulnerabilityTypeChart from '../components/charts/VulnerabilityFrequencyChart';

// Main Page Component
export default function KnowledgePage() {
  const { user } = useAuth(); // Access authenticated user details

  return (
    <Container>
      {/* Page Title */}
      <Typography variant="h3" component="h1" gutterBottom>
        Knowledge Page
      </Typography>

      {/* Welcome Message Section */}
      <Box sx={{ mt: 2 }}>
        <Card>
          <CardContent>
            {/* If user is logged in, show the personalized welcome, else show generic notice */}
            {user ? (
              <Typography variant="body1">
                Welcome {user.name || user.email}! Explore the related articles regarding common vulnerabilities types in C/C++.
              </Typography>
            ) : (
              <Typography variant="body1">
                This is the page to explore common vulnerabilities types in C/C++. Please log in to see personalized content.
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Visualization Card - always visible (provides value even when not logged in) */}
      <Box sx={{ mt: 4 }}>
        <Card>
          <CardContent>
            <Visualization />
          </CardContent>
        </Card>
      </Box>

      {/* Additional detailed content - only for logged in users - else show generic message */}
      {user ? (
        <Box sx={{ mt: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Understanding the Dataset and Common Vulnerability Types
              </Typography>

              <Typography variant="body1">
                As illustrated in the visualizations above, the dataset encompasses a variety of programming languages, 
                with a significant focus on C and C++. Therefore, our team recommends you to use our product to scan for
                vulnerabilities in these languages, and get to know some of the most common vulnerability types found in them.
              </Typography>

              <Typography variant="h6" sx={{ mt: 3 }}>
                🔍 Some of the common types of C/C++ vulnerabilities include:
              </Typography>

              <VulnerabilityKnowledge />

              <Typography variant="body1">
                These vulnerability types are not only common in academic datasets but also 
                frequently reported in real-world software and security advisories. 
                Understanding them helps developers and researchers identify patterns in unsafe code 
                and design better detection models.
              </Typography>

              <Typography variant="h6" sx={{ mt: 3 }}>
                📚 Recommended Reading and Resources
              </Typography>

              <ul>
                <li>
                  <a href="https://cwe.mitre.org/" target="_blank" rel="noopener noreferrer">
                    MITRE Common Weakness Enumeration (CWE)
                  </a> — A comprehensive catalog of software weakness types.
                </li>
                <li>
                  <a href="https://nvd.nist.gov/" target="_blank" rel="noopener noreferrer">
                    NIST National Vulnerability Database (NVD)
                  </a> — Official U.S. government repository of vulnerability data.
                </li>
                <li>
                  <a href="https://owasp.org/www-project-top-ten/" target="_blank" rel="noopener noreferrer">
                    OWASP Top 10
                  </a> — The most critical web application security risks, 
                  many of which relate to unsafe memory and input handling.
                </li>
                <li>
                  <a href="https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard" target="_blank" rel="noopener noreferrer">
                    SEI CERT C Coding Standard
                  </a> — Best practices for secure C programming to prevent common vulnerability classes.
                </li>
                <li>
                  <a href="https://developer.mozilla.org/en-US/docs/Mozilla/Projects/Security/Bug_Classes" target="_blank" rel="noopener noreferrer">
                    Mozilla Developer Network: Common Bug Classes
                  </a> — A readable overview of vulnerability categories and how to avoid them.
                </li>
              </ul>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                By exploring the visualizations and external resources, 
                you can better understand how vulnerabilities arise in low-level languages 
                and what defensive programming practices can mitigate them.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      ) : (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Note: Log in to access additional guidance, examples, and recommended resources.
          </Typography>
        </Box>
      )}
    </Container>
  );
}

// Visualization Component
// Fetches and displays analytical charts for vulnerability data.
const Visualization = () => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // Fetch data for visualizations from backend API
    fetch("http://localhost:8000/api/visualization")
      .then(res => res.json())
      .then(data => setChartData(data))
      .catch(err => console.error("Failed to fetch visualization data:", err));
  }, []);

  // Show loading message until data is fetched
  if (!chartData) return <p>Loading charts...</p>;

  // Render charts when data is ready
  return (
    <div>
      {/* Page Subtitle */}
      <h1 style={{ textAlign: "center" }}>KnowledgePage Dashboard</h1>

      {/* Pie Chart: Language Distribution */}
      <h2>Language Distribution</h2>
      <LangDistributionChart data={chartData.language_distribution} />

      {/* Horizontal Bar Chart: Vulnerability Types */}
      <h2>Vulnerability Types</h2>
      <VulnerabilityTypeChart data={chartData.vuln_type_frequency} />
    </div>
  );
};

// Vulnerabilities Knowledge Component (Accordion-based, detailed explanations and intuitive layout)
const VulnerabilityKnowledge = () => {
  const vulnerabilities = [
    {
      title: 'Heap-Based Buffer Overflow',
      desc: `Occurs when a program writes more data to a heap-allocated memory buffer
             than it was intended to hold. Often caused by unchecked memory copy or
             user input.`,
      impact: `May lead to heap corruption, arbitrary code execution, or denial of service.`,
      mitigation: `Validate buffer sizes, use safer copy functions (strncpy, snprintf),
                   and enable runtime protections such as ASLR and DEP.`
    },
    {
      title: 'Integer Overflow',
      desc: `Triggered when arithmetic operations exceed the numeric bounds of the
              variable type, often leading to incorrect calculations or memory allocation errors.`,
      impact: `Can cause logic errors, buffer overflows, or privilege escalation.`,
      mitigation: `Check arithmetic boundaries, use larger integer types, and enable
                   compiler checks such as -ftrapv.`
    },
    {
      title: 'Uncontrolled Format String',
      desc: `Occurs when user input is unsafely passed as a format string to functions like
             printf(), allowing attackers to control the output format or access memory.`,
      impact: `Can expose sensitive data or even allow arbitrary code execution.`,
      mitigation: `Never use user input directly as a format string. Use "%s" for all
                   external input.`
    },
    {
      title: 'Mismatched Memory Management Routines',
      desc: `Happens when memory allocated with one method (e.g., malloc) is freed using
             another (e.g., delete), leading to undefined behavior.`,
      impact: `May result in memory leaks, corruption, or heap instability.`,
      mitigation: `Always match allocation and deallocation pairs correctly (malloc/free,
                   new/delete) and prefer smart pointers in C++.`
    },
    {
      title: 'Stack-Based Buffer Overflow',
      desc: `Occurs when a program writes more data to a stack buffer than its allocated
             space, overwriting adjacent memory including return addresses.`,
      impact: `Often allows attackers to hijack program control flow or inject shellcode.`,
      mitigation: `Use safer string and memory functions, enable stack canaries, and enforce
                   memory protections.`
    }
  ];

  // Render accordion for each vulnerability
  return (
    <div>
      {vulnerabilities.map((vuln, index) => (
        <Accordion key={index} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={"▼"}>
            <Typography variant="h6">{vuln.title}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Description:</strong> {vuln.desc}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Impact:</strong> {vuln.impact}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Mitigation:</strong> {vuln.mitigation}
            </Typography>
            <Typography variant="body2">
              <strong>Learn more:</strong>{' '}
              <Link href={vuln.link} target="_blank" rel="noopener">
                {vuln.link}
              </Link>
            </Typography>
          </AccordionDetails>
        </Accordion>
      ))}
    </div>
  );
};
