import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position, useUpdateNodeInternals } from '@xyflow/react';


const functionsList = [
  { name: 'Human-in-the-loop', fn: () => console.log('Human-in-the-loop node') },
  { name: 'Human-approval', fn: () => console.log('Human-approval node') },
  { name: 'Parse input', fn: () => console.log('Parse input node') },
  { name: 'General computer interaction', fn: () => console.log('Explaining...') },
  { name: 'Researcher', fn: () => console.log('Researching...') },
  { name: 'Timing', fn: () => console.log('Timing...') },
  { name: 'End', fn: () => console.log('Generating code...') },
];

const handleStyle = { left: 10 };

function TextUpdaterNode({ id, data }) {
  const [text, setText] = useState(data.text || '');
  const [includedFunctions, setIncludedFunctions] = useState(data.functions || []);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const textareaRef = useRef(null);
  const updateNodeInternals = useUpdateNodeInternals();

  // Sync back to node data so it can be extracted
  useEffect(() => {
    data.text = text;
    data.functions = includedFunctions;
    updateNodeInternals(id);
  }, [text, includedFunctions]);

  const handleChange = (e) => {
    const value = e.target.value;
    setText(value);

    const lastChar = value.slice(-1);
    if (lastChar === '/') {
      const rect = textareaRef.current.getBoundingClientRect();
      setDropdownPosition({ top: rect.top + 24, left: rect.left + 10 });
      setShowDropdown(true);
    } else if (!value.includes('/')) {
      setShowDropdown(false);
    }
  };

  const handleFunctionClick = (func) => {
    const newText = text.replace(/\/$/, `{{${func.name}}}`);
    setText(newText);
    setIncludedFunctions((prev) => [...prev, func]);
    setShowDropdown(false);
  };

  return (
    <>
      <Handle type="target" position={Position.Top} />
      <div style={{ position: 'relative', padding: 8, backgroundColor: '#fff', borderRadius: 4, border: '1px solid #ccc' }}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleChange}
          rows={3}
          className="nodrag"
          placeholder="Type '/' to see functions..."
          style={{ width: '100%', resize: 'both', fontSize: 14 }}
        />
        {showDropdown && (
          <ol
            style={{
              position: 'absolute',
              top: dropdownPosition.top - textareaRef.current.getBoundingClientRect().top + 40,
              left: dropdownPosition.left - textareaRef.current.getBoundingClientRect().left,
              backgroundColor: '#f9f9f9',
              border: '1px solid #ccc',
              borderRadius: 4,
              listStyle: 'none',
              padding: 8,
              margin: 0,
              width: 150,
              zIndex: 10,
            }}
          >
            {functionsList.map((func) => (
              <li
                key={func.name}
                onClick={() => handleFunctionClick(func)}
                style={{
                  padding: 4,
                  cursor: 'pointer',
                  borderBottom: '1px solid #eee',
                }}
              >
                {func.name}
              </li>
            ))}
          </ol>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} id="a" />
    </>
  );
}

export default TextUpdaterNode;
