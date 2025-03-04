document.addEventListener("DOMContentLoaded", function() {
    // Global arrays to store selected cards.
    let selectedPlayerHand = [];
    let selectedCommunityCards = [];
    let activeSlot = null;  // For manual assignment
    let debounceTimeout;
  
    // Define the 13 ranks (ordered high-to-low) and the four suits.
    const ranks = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];
    const suits = ['c','d','h','s'];
  
    // --- Populate the Deck ---
    const deckContainer = document.getElementById("deck");
    ranks.forEach(rank => {
      const cardCode = rank + 'c';  // clubs as representative
      let div = document.createElement("div");
      div.classList.add("deck-card");
      div.dataset.rank = rank;
      let img = document.createElement("img");
      img.src = "static/cards/" + cardCode + ".png";
      img.alt = rank;
      div.appendChild(img);
      // Single click: show suit options inline.
      div.addEventListener("click", function(e) {
        e.stopPropagation();
        showSuitOptions(div, rank);
      });
      // Double-click: auto-assign default suit (clubs).
      div.addEventListener("dblclick", function(e) {
        e.stopPropagation();
        selectCard(rank + 'c');
      });
      deckContainer.appendChild(div);
    });
  
    // --- Show Suit Options Inline (All Suits at Once) ---
    function showSuitOptions(parentDiv, rank) {
      const suitContainer = document.getElementById("suitOptionsContainer");
      suitContainer.innerHTML = "";
      suitContainer.style.display = "block";
      const rect = parentDiv.getBoundingClientRect();
      suitContainer.style.top = (rect.bottom + window.scrollY + 5) + "px";
      suitContainer.style.left = (rect.left + window.scrollX) + "px";
      
      suits.forEach(suit => {
        let cardCode = rank + suit;
        let option = document.createElement("img");
        option.src = "static/cards/" + cardCode + ".png";
        option.alt = cardCode;
        option.classList.add("suit-option");
        option.addEventListener("click", function(e) {
          e.stopPropagation();
          selectCard(cardCode);
          suitContainer.style.display = "none";
        });
        suitContainer.appendChild(option);
      });
      document.addEventListener("click", function handler() {
        suitContainer.style.display = "none";
        document.removeEventListener("click", handler);
      });
    }
  
    // --- Select Card Function ---
    function selectCard(card) {
      if (activeSlot) {
        activeSlot.style.backgroundImage = "url(static/cards/" + card + ".png)";
        activeSlot.dataset.card = card;
        updateSelectionArray(activeSlot, card);
        activeSlot.classList.remove("active-slot");
        activeSlot = null;
      } else {
        if (selectedPlayerHand.length < 2) {
          selectedPlayerHand.push(card);
          updateSlots("playerHandSlots", selectedPlayerHand);
        } else if (selectedCommunityCards.length < 5) {
          selectedCommunityCards.push(card);
          updateSlots("communityCardsSlots", selectedCommunityCards);
        } else {
          // If 5 community cards are already selected, clear them and start over.
          selectedCommunityCards = [];
          updateSlots("communityCardsSlots", selectedCommunityCards);
          selectedCommunityCards.push(card);
          updateSlots("communityCardsSlots", selectedCommunityCards);
        }
      }
      triggerCalculation();
    }
  
    // --- Update Selection Array for a Given Slot ---
    function updateSelectionArray(slot, card) {
      if (slot.parentNode.id === "playerHandSlots") {
        const slots = Array.from(document.getElementById("playerHandSlots").children);
        let index = slots.indexOf(slot);
        selectedPlayerHand[index] = card;
      } else if (slot.parentNode.id === "communityCardsSlots") {
        const slots = Array.from(document.getElementById("communityCardsSlots").children);
        let index = slots.indexOf(slot);
        selectedCommunityCards[index] = card;
      }
    }
  
    // --- Update Slot Displays ---
    function updateSlots(slotId, selectedArray) {
      const container = document.getElementById(slotId);
      const slots = container.querySelectorAll(".card-slot");
      for (let i = 0; i < slots.length; i++) {
        if (selectedArray[i]) {
          slots[i].style.backgroundImage = "url(static/cards/" + selectedArray[i] + ".png)";
          slots[i].dataset.card = selectedArray[i];
        } else {
          slots[i].style.backgroundImage = "";
          slots[i].dataset.card = "";
        }
      }
    }
  
    // --- Slot Click: Activate for Manual Assignment ---
    document.querySelectorAll(".card-slot").forEach(slot => {
      slot.addEventListener("click", function() {
        document.querySelectorAll(".card-slot").forEach(s => s.classList.remove("active-slot"));
        activeSlot = slot;
        slot.classList.add("active-slot");
      });
    });
  
    // --- Drag-and-Drop for Slots ---
    function enableDragAndDrop() {
      const slots = document.querySelectorAll(".card-slot");
      slots.forEach(slot => {
        slot.addEventListener("dragover", function(e) {
          e.preventDefault();
          slot.classList.add("drag-over");
        });
        slot.addEventListener("dragleave", function(e) {
          slot.classList.remove("drag-over");
        });
        slot.addEventListener("drop", function(e) {
          e.preventDefault();
          slot.classList.remove("drag-over");
          let card = e.dataTransfer.getData("text/plain");
          slot.style.backgroundImage = "url(static/cards/" + card + ".png)";
          slot.dataset.card = card;
          updateSelectionArray(slot, card);
        });
      });
    }
    enableDragAndDrop();
  
    // --- Enable Drag for Suit Options (Dropdown) Cards ---
    document.getElementById("suitOptionsContainer").addEventListener("mouseover", function() {
      const dropdownCards = document.querySelectorAll(".suit-option");
      dropdownCards.forEach(cardImg => {
        cardImg.draggable = true;
        cardImg.addEventListener("dragstart", function(e) {
          e.dataTransfer.setData("text/plain", cardImg.alt);
        });
      });
    });
  
    // --- Quick Entry for Player Hand ---
    document.getElementById("quick_hand_entry").addEventListener("keydown", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const handString = this.value.trim();
        if (handString.length !== 4) {
          alert("Please enter exactly 4 characters (e.g., AcKd).");
          return;
        }
        const card1 = handString.substring(0,2);
        const card2 = handString.substring(2,4);
        selectedPlayerHand = [card1, card2];
        updateSlots("playerHandSlots", selectedPlayerHand);
        this.value = "";
        triggerCalculation();
      }
    });
  
    // --- Quick Entry for Community Cards ---
    document.getElementById("quick_comm_entry").addEventListener("keydown", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const commString = this.value.trim();
        if (commString.length !== 2) {
          alert("Please enter a 2-character code for the community card (e.g., 7h).");
          return;
        }
        if (selectedCommunityCards.length < 5) {
          selectedCommunityCards.push(commString);
        } else {
          selectedCommunityCards = [commString];
        }
        updateSlots("communityCardsSlots", selectedCommunityCards);
        this.value = "";
        triggerCalculation();
      }
    });
  
    // --- Real-Time Calculation (Debounced) ---
    function triggerCalculation() {
      if (debounceTimeout) clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(calculateResults, 500);
    }
  
    function calculateResults() {
      if (selectedPlayerHand.length !== 2) return;
      const numOpponents = parseInt(document.getElementById("num_opponents").value);
      const potSize = parseFloat(document.getElementById("pot_size_range").value);
      const callAmount = parseFloat(document.getElementById("call_amount_range").value);
      const payload = {
        player_hand: selectedPlayerHand,
        community_cards: selectedCommunityCards,
        num_opponents: numOpponents,
        pot_size: potSize,
        call_amount: callAmount,
        simulations: 10000
      };
  
      fetch("/api/poker_decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
      .then(response => response.json())
      .then(data => {
        let drawAnalysisHTML = '<ul>';
        drawAnalysisHTML += `<li><strong>Flush Draw:</strong> ${data.draw_analysis.flush_draw ? "Yes" : "No"}</li>`;
        drawAnalysisHTML += `<li><strong>Straight Draw:</strong> ${data.draw_analysis.straight_draw ? "Yes" : "No"}</li>`;
        drawAnalysisHTML += `<li><strong>Total Outs:</strong> ${data.draw_analysis.outs}</li>`;
        drawAnalysisHTML += `<li><strong>Estimated Draw Probability:</strong> ${data.draw_analysis.draw_probability}%</li>`;
        drawAnalysisHTML += '</ul>';
  
        document.getElementById("results").innerHTML = `
          <div class="result-card">
            <p><strong>Win Probability:</strong> ${data.win_probability.toFixed(2)}%</p>
            <p><strong>Break-even Equity:</strong> ${data.break_even_equity.toFixed(2)}%</p>
            <p><strong>EV Decision:</strong> ${data.ev_decision}</p>
            <p><strong>Hand Strength:</strong> ${data.hand_strength}</p>
            <div>
              <strong>Draw Analysis:</strong>
              ${drawAnalysisHTML}
            </div>
          </div>
        `;
      })
      .catch(error => {
        console.error("Error:", error);
        document.getElementById("results").innerHTML = "<p>An error occurred.</p>";
      });
    }
  
    // --- Clear Hand Button: Reset all selections ---
    document.getElementById("clearHandBtn").addEventListener("click", function() {
      selectedPlayerHand = [];
      selectedCommunityCards = [];
      updateSlots("playerHandSlots", selectedPlayerHand);
      updateSlots("communityCardsSlots", selectedCommunityCards);
      triggerCalculation();
    });
  
    // --- Event Listeners for Left Panel Settings ---
    document.getElementById("pot_size_range").addEventListener("input", function() {
      document.getElementById("pot_size_display").innerText = this.value;
      triggerCalculation();
    });
    document.getElementById("call_amount_range").addEventListener("input", function() {
      document.getElementById("call_amount_display").innerText = this.value;
      triggerCalculation();
    });
    document.getElementById("opp-decrease").addEventListener("click", function() {
      let input = document.getElementById("num_opponents");
      input.value = Math.max(1, parseInt(input.value) - 1);
      triggerCalculation();
    });
    document.getElementById("opp-increase").addEventListener("click", function() {
      let input = document.getElementById("num_opponents");
      input.value = parseInt(input.value) + 1;
      triggerCalculation();
    });
    document.querySelectorAll(".preset").forEach(button => {
      button.addEventListener("click", function() {
        document.getElementById("pot_size_range").value = this.dataset.pot;
        document.getElementById("pot_size_display").innerText = this.dataset.pot;
        document.getElementById("call_amount_range").value = this.dataset.call;
        document.getElementById("call_amount_display").innerText = this.dataset.call;
        triggerCalculation();
      });
    });
  });
  