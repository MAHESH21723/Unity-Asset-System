using System;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Simple slot-limited inventory that stacks items by id.
/// </summary>
public class InventoryManager : MonoBehaviour
{
    public static InventoryManager Instance { get; private set; }

    [Serializable]
    public struct Item
    {
        public string id;
        public string displayName;
        public int amount;
    }

    [SerializeField] private List<Item> items = new List<Item>();
    [SerializeField] private int maxCapacity = 20;

    /// <summary>Raised whenever the inventory contents change.</summary>
    public event Action InventoryChanged;

    public IReadOnlyList<Item> Items => items;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
    }

    public bool AddItem(Item newItem)
    {
        int index = items.FindIndex(i => i.id == newItem.id);
        if (index >= 0)
        {
            Item stacked = items[index];
            stacked.amount += newItem.amount;
            items[index] = stacked;
        }
        else
        {
            if (items.Count >= maxCapacity)
            {
                Debug.LogWarning("Inventory full!");
                return false;
            }

            items.Add(newItem);
        }

        Debug.Log($"Added {newItem.amount}x {newItem.displayName} to inventory.");
        InventoryChanged?.Invoke();
        return true;
    }

    public bool RemoveItem(string itemId, int amount)
    {
        int index = items.FindIndex(i => i.id == itemId);
        if (index < 0 || items[index].amount < amount) return false;

        Item stacked = items[index];
        stacked.amount -= amount;
        if (stacked.amount <= 0)
        {
            items.RemoveAt(index);
        }
        else
        {
            items[index] = stacked;
        }

        InventoryChanged?.Invoke();
        return true;
    }
}
