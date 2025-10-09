import React, { useState, useEffect } from "react";

const LoadingSpinner = ({ type = "flowchart", text, subText }) => {
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Default texts based on type
  const defaultText = type === "testCases" ? "Generating Test Cases" : "Generating Flowchart";
  const defaultSubText = type === "testCases" ? "Analyzing flowchart paths..." : "Building from test cases...";

  const displayText = text || defaultText;
  const displaySubText = subText || defaultSubText;

  // Simulate progress and track elapsed time
  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedTime(elapsed);

      // Simulate progress based on elapsed time (not real progress, just visual)
      if (elapsed < 10) {
        setProgress(Math.min(20 + elapsed * 3, 30));
      } else if (elapsed < 30) {
        setProgress(Math.min(30 + (elapsed - 10) * 2, 60));
      } else if (elapsed < 60) {
        setProgress(Math.min(60 + (elapsed - 30) * 1, 85));
      } else {
        setProgress(Math.min(85 + (elapsed - 60) * 0.5, 95));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getEstimatedTime = () => {
    if (elapsedTime < 10) return "Estimated time: 1-2 minutes";
    if (elapsedTime < 30) return "Estimated time: 30-60 seconds remaining";
    if (elapsedTime < 60) return "Almost done...";
    return "Processing...";
  };

  if (type === "testCases") {
    return (
      <div className="loader-container-tc">
        <div className="flowchart-container-tc">
          {/* Flowchart Nodes */}
          <div className="node-tc start">START</div>
          <div className="node-tc decision">
            <span>Check</span>
          </div>
          <div className="node-tc process1">Path A</div>
          <div className="node-tc process2">Path B</div>
          <div className="node-tc end">END</div>

          {/* Connecting Lines */}
          <div className="line-tc vertical1"></div>
          <div className="line-tc diagonal-left"></div>
          <div className="line-tc diagonal-right"></div>
          <div className="line-tc vertical2"></div>

          {/* Test Case Cards */}
          <div className="test-cases-tc">
            <div className="test-card-tc">TC-01</div>
            <div className="test-card-tc">TC-02</div>
            <div className="test-card-tc">TC-03</div>
            <div className="test-card-tc">TC-04</div>
          </div>

          {/* Robot Assistant */}
          <div className="robot-assistant-tc">
            <div className="robot-head-tc">
              <div className="robot-antenna-tc"></div>
              <div className="robot-eye-tc left"></div>
              <div className="robot-eye-tc right"></div>
            </div>
          </div>
        </div>

        <div className="status-container-tc">
          <div className="status-text-tc">{displayText}</div>
          <div className="progress-bar-tc">
            <div className="progress-fill-tc" style={{ width: `${progress}%` }}></div>
          </div>
          <div className="sub-text-tc">{displaySubText}</div>
          <div className="time-info-tc">
            <div className="elapsed-time-tc">Elapsed: {formatTime(elapsedTime)}</div>
            <div className="estimated-time-tc">{getEstimatedTime()}</div>
          </div>
        </div>
      </div>
    );
  }

  // Flowchart loader (existing)
  return (
    <div className="loader-container">
      <div className="construction-area">
        {/* Test Documents Flying In */}
        <div className="test-documents">
          <div className="test-doc"></div>
          <div className="test-doc"></div>
          <div className="test-doc"></div>
          <div className="test-doc"></div>
        </div>

        {/* Central Processing Brain */}
        <div className="processing-brain">
          <div className="brain-icon">
            <div className="brain-wave"></div>
            <div className="brain-wave"></div>
            <div className="brain-wave"></div>
          </div>
        </div>

        {/* Flowchart Nodes Being Built */}
        <div className="building-nodes">
          <div className="building-node">
            <div className="node-shape">START</div>
          </div>
          <div className="building-node">
            <div className="node-shape"></div>
          </div>
          <div className="building-node">
            <div className="node-shape">Step 1</div>
          </div>
          <div className="building-node">
            <div className="node-shape">Step 2</div>
          </div>
          <div className="building-node">
            <div className="node-shape">END</div>
          </div>
        </div>

        {/* Connection Lines Being Drawn */}
        <div className="drawing-line line1"></div>
        <div className="drawing-line line2"></div>

        {/* Robot Builder */}
        <div className="robot-builder">
          <div className="robot-body">
            <div className="robot-head-small">
              <div className="robot-eye-small left"></div>
              <div className="robot-eye-small right"></div>
            </div>
            <div className="robot-arm left"></div>
            <div className="robot-arm right"></div>
          </div>
        </div>
      </div>

      <div className="status-container">
        <div className="status-text">{displayText}</div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
        <div className="sub-text">{displaySubText}</div>
        <div className="time-info">
          <div className="elapsed-time">Elapsed: {formatTime(elapsedTime)}</div>
          <div className="estimated-time">{getEstimatedTime()}</div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
