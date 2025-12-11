// FOR DROPDOWN IN TEXT AREA IN NODE TEXT

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
  { name: 'Conditional', fn: () => console.log('Conditional node') }
];

const handleStyle = { left: 10 };

function TextUpdaterNode({ id, data }) {
  const [text, setText] = useState(data.text || '');
  const [includedFunctions, setIncludedFunctions] = useState(data.functions || []);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const textareaRef = useRef(null);
  const updateNodeInternals = useUpdateNodeInternals();

  // Filter functions based on search term
  const filteredFunctions = searchTerm 
    ? functionsList.filter(func => 
        func.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : functionsList;

  // Sync back to node data so it can be extracted
  useEffect(() => {
    data.text = text;
    data.functions = includedFunctions;
    updateNodeInternals(id);
  }, [text, includedFunctions]);

  const handleChange = (e) => {
    const value = e.target.value;
    setText(value);

    // Check if there's a slash and extract the search term after it
    const slashIndex = value.lastIndexOf('/');
    if (slashIndex !== -1) {
      const searchAfterSlash = value.substring(slashIndex + 1);
      setSearchTerm(searchAfterSlash);
      
      if (slashIndex === value.length - 1) {
        // Just typed a slash, show dropdown
        const rect = textareaRef.current.getBoundingClientRect();
        setDropdownPosition({ top: rect.top + 24, left: rect.left + 10 });
        setShowDropdown(true);
        setSelectedIndex(0);
      } else if (searchAfterSlash.length >= 0) {
        // Typing after slash, keep dropdown open and reset selection
        setShowDropdown(true);
        setSelectedIndex(0);
      }
    } else {
      // No slash in text, hide dropdown
      setShowDropdown(false);
      setSelectedIndex(0);
      setSearchTerm('');
    }
  };

  const handleKeyDown = (e) => {
    if (showDropdown && filteredFunctions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredFunctions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredFunctions.length) % filteredFunctions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        handleFunctionClick(filteredFunctions[selectedIndex]);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        setShowDropdown(false);
        setSelectedIndex(0);
        setSearchTerm('');
      }
    }
  };

  const handleFunctionClick = (func) => {
    // replace the slash stuff with dropdown choices
    const slashIndex = text.lastIndexOf('/');
    const newText = text.substring(0, slashIndex) + `{{${func.name}}}`;
    setText(newText);
    setIncludedFunctions((prev) => [...prev, func]);
    setShowDropdown(false);
    setSearchTerm('');
    setSelectedIndex(0);
  };

  return (
    <>
      <Handle type="target" position={Position.Top} />
      <div style={{ position: 'relative', padding: 8, backgroundColor: '#fff', borderRadius: 4, border: '1px solid #ccc' }}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
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
            {filteredFunctions.map((func, index) => (
              <li
                key={func.name}
                onClick={() => handleFunctionClick(func)}
                style={{
                  padding: 4,
                  cursor: 'pointer',
                  borderBottom: '1px solid #eee',
                  backgroundColor: index === selectedIndex ? '#e6f3ff' : 'transparent',
                  color: index === selectedIndex ? '#0066cc' : 'inherit',
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
