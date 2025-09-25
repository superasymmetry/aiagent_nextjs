import React, { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';
import TextUpdaterNode from './TextUpdaterNode.jsx';
import ButtonEdge from './ButtonEdge';
import axios from 'axios';
import Modal from './components/Modal.jsx';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import Popup from 'reactjs-popup';


const nodeTypes = {
  textUpdater: TextUpdaterNode
};

const edgeTypes = {
  buttonedge: ButtonEdge,
};

// may use to toggle dark mode
const rfStyle = {
  backgroundColor: '#B8CEFF',
};

const initialNodes = [
  { id: '1', type: 'textUpdater', position: { x: 400, y: 50 }, data: { text: '' } },
  { id: '2', type: 'textUpdater', position: { x: 400, y: 200 }, data: { text: '' } }
];

const initialEdges = [
  { id: 'edge1', source: '1', target: '2', type: 'buttonedge' }
];

// const centerX = 600;
// const centerY = 300;
// const radius = 250;

// // Using 8 child nodes evenly spaced (every 45°)
// const rad = Math.PI / 4; // 45 degrees in radians
// const initialNodes = [
//   { id: 'main', type: 'textUpdater', position: { x: centerX, y: centerY }, data: { text: 'Master Agent' } },
//   { id: 'child1', type: 'textUpdater', position: { x: centerX + radius, y: centerY }, data: { text: '' } },                    // 0°
//   { id: 'child2', type: 'textUpdater', position: { x: centerX + Math.round(radius * Math.cos(rad)), y: centerY + Math.round(radius * Math.sin(rad)) }, data: { text: '' } }, // 45°
//   { id: 'child3', type: 'textUpdater', position: { x: centerX, y: centerY + radius }, data: { text: '' } },                              // 90°
//   { id: 'child4', type: 'textUpdater', position: { x: centerX - Math.round(radius * Math.cos(rad)), y: centerY + Math.round(radius * Math.sin(rad)) }, data: { text: '' } }, // 135°
//   { id: 'child5', type: 'textUpdater', position: { x: centerX - radius, y: centerY }, data: { text: '' } },                               // 180°
//   { id: 'child6', type: 'textUpdater', position: { x: centerX - Math.round(radius * Math.cos(rad)), y: centerY - Math.round(radius * Math.sin(rad)) }, data: { text: '' } }, // 225°
//   { id: 'child7', type: 'textUpdater', position: { x: centerX, y: centerY - radius }, data: { text: '' } },                               // 270°
//   { id: 'child8', type: 'textUpdater', position: { x: centerX + Math.round(radius * Math.cos(rad)), y: centerY - Math.round(radius * Math.sin(rad)) }, data: { text: '' } }, // 315°
// ];

// const initialEdges = [
//   { id: 'edge1', source: 'main', target: 'child1', type: 'buttonedge' },
//   { id: 'edge2', source: 'main', target: 'child2', type: 'buttonedge' },
//   { id: 'edge3', source: 'main', target: 'child3', type: 'buttonedge' },
//   { id: 'edge4', source: 'main', target: 'child4', type: 'buttonedge' },
//   { id: 'edge5', source: 'main', target: 'child5', type: 'buttonedge' },
//   { id: 'edge6', source: 'main', target: 'child6', type: 'buttonedge' },
//   { id: 'edge7', source: 'main', target: 'child7', type: 'buttonedge' },
//   { id: 'edge8', source: 'main', target: 'child8', type: 'buttonedge' },
// ];

export default function App() {
  const [showModal, setShowModal] = useState(false);
  const [array, setArray] = useState([]);
  const fetchAPI = async () => {
    const response = await axios.get('http://localhost:8080/api/graph');
    setArray(response.data);
    console.log(response.data);
  }

  useEffect(() => {
    fetchAPI();
  }, []);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodeIdCounter, setNodeIdCounter] = useState(6);

  const onConnect = useCallback(
    (params) =>
      setEdges((eds) =>
        addEdge({ ...params, type: 'buttonedge' }, eds)
      ),
    [setEdges]
  );

  const handleNodeRightClick = (event, node) => {
    event.preventDefault();
    setSelectedNode(node);
  };

  // Update node details
  const handleDetailChange = (e) => {
    const newDetail = e.target.value;
    setNodes((nds) =>
      nds.map((node) =>
        node.id === selectedNode.id
          ? { ...node, data: { ...node.data, details: newDetail } }
          : node
      )
    );
  };

  // delete node
  const deleteNode = (nodeId) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
  };
  
  const addNode = () => {
    const newNode = {
      id: `${nodeIdCounter}`,
      type: 'textUpdater',
      position: { x: Math.random() * 250, y: Math.random() * 400 },
      data: { value: 123 },
    };
    setNodes((nds) => [...nds, newNode]);
    setNodeIdCounter((id) => id + 1);
  };
  
  const [progress, setProgress] = useState([]);
  // extract graph
  const handleExport = async () => {
    const nodeTexts = nodes.map((node) => ({
      id: node.id,
      text: node.data.text || '',  // Adjust depending on what you're storing
    }));
    const graphData = {
      nodeTexts,
      edges,
    };
  
    console.log('Exported Graph:', graphData);
    // JSON.stringify(graphData, null, 2);
    setProgress([]);  // Clear previous progress

  await fetchEventSource('http://localhost:8080/api/graph', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(graphData),
    onmessage(msg) {
      if (msg.event === 'end') {
        console.log('Stream finished');
        return;
      }
      
      if (msg.data.includes('humanquestion') || msg.data.includes('HUMAN_INPUT') || msg.data.includes('{{human}}')) {
        const userInput = window.prompt('Human interruption input: ', 'Type response here...');
        if (userInput !== null) {
          console.log('User input:', userInput);
          // Send the user input back to the server
          
        }
      } else {
        setProgress((prev) => [...prev, msg.data]);
      }
    },
    onerror(err) {
      console.error('Streaming error:', err);
    },
  });
  };

  // Modal
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setShowModal(false);
  };

  return (
    // Main container
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
    <Popup trigger={<button> Templates</button>} position="right center">
      <Modal onClose={() => setShowModal(false)} onSelectTemplate = {handleTemplateSelect} />
      {/* <div>Popup content here !!</div> */}
    </Popup>
      {/* Right Sidebar for LangGraph Progress */}
      <div
        style={{
          width: '300px',
          height: '100vh',
          backgroundColor: '#f8f9fa',
          borderLeft: '1px solid #ccc',
          padding: '16px',
          overflowY: 'auto',
          boxSizing: 'border-box',
          fontFamily: 'monospace',
        }}
      >
        <h4 style={{ color: '#333', marginBottom: '12px' }}>Execution Progress</h4>
        {progress.length === 0 ? (
          <p style={{ color: '#999' }}>No progress yet.</p>
        ) : (
          progress.map((line, index) => (
            <div
              key={index}
              style={{
                backgroundColor: '#e9efff',
                padding: '8px',
                marginBottom: '8px',
                borderRadius: '6px',
                borderLeft: '4px solid #007bff',
                whiteSpace: 'pre-wrap',
                color: '#212529',
              }}
            >
              {line}
            </div>
          ))
        )}
      </div>

      {/* Sidebar */}
      {selectedNode && (
        <div
          style={{
            width: 250,
            background: '#f4f4f4',
            padding: 16,
            borderRight: '1px solid #ccc',
          }}
        >
          <h4>Edit Node {selectedNode.id}</h4>
          <button onClick={() => setSelectedNode(null)}>Close</button>
          <button onClick={() => deleteNode(selectedNode.id)}>Delete</button>

        </div>
      )}

      {/* Flow Canvas */}
      <div style={{ flex: 1 }}>
        <button
          onClick={addNode}
          style={{
            position: 'absolute',
            zIndex: 10,
            left: 50,
            top: 740,
            padding: '8px 12px',
            borderRadius: '8px',
            border: 'none',
            background: '#333',
            color: '#fff',
            cursor: 'pointer',
          }}
        >
          Add Node
        </button>
        <button
          onClick={handleExport}
          style={{
            position: 'absolute',
            zIndex: 10,
            left: 150,
            top: 740,
            padding: '8px 12px',
            borderRadius: '8px',
            border: 'none',
            background: '#007bff',
            color: '#fff',
            cursor: 'pointer',
          }}
        >
          Execute Flow
        </button>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodeContextMenu={handleNodeRightClick}
          
        >
          <Controls />
          <MiniMap />
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
}
