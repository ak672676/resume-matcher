import React, { useState, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function RolesPage() {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [addingRole, setAddingRole] = useState(false);
  const [deletingRole, setDeletingRole] = useState('');

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/roles`);
      const data = await res.json();
      setRoles(data.roles || []);
    } catch (err) {
      console.error('Failed to fetch roles:', err);
      setMessage('Failed to fetch roles');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRole = async () => {
    if (!newRole.trim()) return;
    
    setAddingRole(true);
    try {
      const res = await fetch(`${API_BASE_URL}/roles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          name: newRole.trim(),
          description: newDescription.trim()
        }),
      });
      const data = await res.json();
      
      if (res.ok) {
        setNewRole('');
        setNewDescription('');
        fetchRoles(); // Refresh roles list
        setMessage(`Role "${newRole.trim()}" added successfully!`);
      } else {
        setMessage(data.detail || 'Failed to add role');
      }
    } catch (err) {
      console.error('Add role error:', err);
      setMessage('Failed to add role');
    } finally {
      setAddingRole(false);
    }
  };

  const handleDeleteRole = async (roleName) => {
    if (!confirm(`Are you sure you want to delete the role "${roleName}"?`)) {
      return;
    }
    
    setDeletingRole(roleName);
    try {
      const res = await fetch(`${API_BASE_URL}/roles/${encodeURIComponent(roleName)}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      
      if (res.ok) {
        fetchRoles(); // Refresh roles list
        setMessage(`Role "${roleName}" deleted successfully!`);
      } else {
        setMessage(data.detail || 'Failed to delete role');
      }
    } catch (err) {
      console.error('Delete role error:', err);
      setMessage('Failed to delete role');
    } finally {
      setDeletingRole('');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Roles Management</h2>
        <p>Loading roles...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Roles Management</h2>
        <button
          onClick={fetchRoles}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Refresh
        </button>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded ${
          message.includes('successfully') 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        }`}>
          {message}
        </div>
      )}

      {/* Add New Role Form */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
        <h3 className="text-lg font-medium mb-3">Add New Role</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="Role name..."
            value={newRole}
            onChange={(e) => setNewRole(e.target.value)}
            className="px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleAddRole()}
          />
          <input
            type="text"
            placeholder="Description (optional)..."
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            className="px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && handleAddRole()}
          />
          <button
            onClick={handleAddRole}
            disabled={addingRole || !newRole.trim()}
            className={`px-4 py-2 rounded text-white ${
              addingRole || !newRole.trim()
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-green-500 hover:bg-green-600'
            }`}
          >
            {addingRole ? 'Adding...' : 'Add Role'}
          </button>
        </div>
      </div>

      {/* Roles List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-medium">Available Roles ({roles.length})</h3>
        </div>
        
        {roles.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No roles found. Add your first role above.
          </div>
        ) : (
          <div className="divide-y">
            {roles.map((role) => (
              <div key={role.name} className="px-6 py-4 flex justify-between items-center">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{role.name}</h4>
                  {role.description && (
                    <p className="text-sm text-gray-600 mt-1">{role.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteRole(role.name)}
                  disabled={deletingRole === role.name}
                  className={`ml-4 px-3 py-1 text-sm rounded ${
                    deletingRole === role.name
                      ? 'bg-gray-300 cursor-not-allowed'
                      : 'bg-red-500 hover:bg-red-600 text-white'
                  }`}
                >
                  {deletingRole === role.name ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 