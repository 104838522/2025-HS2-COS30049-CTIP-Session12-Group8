import React, { useEffect, useMemo, useState } from "react";
import {
  Container,
  Tabs,
  Tab,
  Typography,
  Box,
  Alert,
  LinearProgress,
} from "@mui/material";

const TAB_CONFIG = [
  {
    label: "Data Collection",
    src: "/assets/dataset/data-collection.pdf",
  },
  {
    label: "Data Processing",
    src: "/assets/dataset/data-processing.pdf",
  },
  {
    label: "Data Analysis",
    src: "/assets/dataset/data-analysis.pdf",
  },
];

const PdfViewer = ({ src }) => (
  <Box
    sx={{
      flex: 1,
      borderRadius: 2,
      overflow: "hidden",
      bgcolor: "background.paper",
      boxShadow: 3,
    }}
  >
    <iframe
      title={src}
      src={`${src}#view=FitH`}
      width="100%"
      height="100%"
      style={{ border: "none", minHeight: 470 }}
    />
  </Box>
);

export default function DatasetInfoPage() {
  const [tab, setTab] = useState(0);
  const [pdfReady, setPdfReady] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const activeConfig = useMemo(() => TAB_CONFIG[tab], [tab]);

  useEffect(() => {
    let cancelled = false;
    setPdfReady(false);
    setPdfError(null);

    fetch(activeConfig.src, { method: "HEAD" })
      .then((res) => {
        if (!cancelled) {
          if (res.ok) {
            setPdfReady(true);
          } else {
            setPdfError(
              `The PDF at "${activeConfig.src}" could not be found (HTTP ${res.status}).`
            );
          }
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPdfError(
            `The PDF at "${activeConfig.src}" could not be loaded. Ensure it exists in the public/assets/dataset folder.`
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeConfig]);

  return (
    <Container
      component="main"
      sx={{
        mt: 2,
        mb: 2,
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        maxWidth: "lg",
      }}
    >
      <Box
        sx={{
          width: "100%",
          flex: 1,
          bgcolor: "grey.100",
          borderRadius: 3,
          boxShadow: 3,
          p: 2,
          display: "flex",
          flexDirection: "column",
          height: 570,
        }}
      >
        <Tabs
          value={tab}
          onChange={(_, value) => setTab(value)}
          textColor="primary"
          indicatorColor="primary"
          variant="fullWidth"
          sx={{ mb: 0.75, '& .MuiTab-root': { minHeight: 28, paddingY: 0.25, fontSize: '0.82rem' } }}
        >
          {TAB_CONFIG.map((item) => (
            <Tab key={item.label} label={item.label} />
          ))}
        </Tabs>

        {!pdfReady && !pdfError && <LinearProgress sx={{ mb: 1 }} />}

        {pdfError ? (
          <Alert severity="warning">
            {pdfError} Place the PDF in `public/assets/dataset/` or update the
            path in `DatasetInfoPage.js`.
          </Alert>
        ) : pdfReady ? (
          <PdfViewer src={activeConfig.src} />
        ) : (
          <Box
            sx={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Loading preview…
            </Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
}
