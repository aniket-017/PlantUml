import React from "react";

const LoadingSpinner = ({ type = "flowchart", text, subText }) => {
  // Default texts based on type
  const defaultText = type === "testCases" ? "Generating Test Cases" : "Generating Flowchart";
  const defaultSubText = type === "testCases" ? "Analyzing flowchart paths..." : "Building from test cases...";

  const displayText = text || defaultText;
  const displaySubText = subText || defaultSubText;

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
            <div className="progress-fill-tc"></div>
          </div>
          <div className="sub-text-tc">{displaySubText}</div>
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
          <div className="progress-fill"></div>
        </div>
        <div className="sub-text">{displaySubText}</div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
