`timescale 1ns/1ps
`include "uvm_macros.svh"

// Define default width if not specified
`ifndef WIDTH
  `define WIDTH 8
`endif

package my_pkg;
  import uvm_pkg::*;

  // Transaction: Input Vector + Expected Index
  class input_item extends uvm_sequence_item;
    rand logic [`WIDTH-1:0] input_vec;
    logic [$clog2(`WIDTH)-1:0] expected_idx;
    
    function new(string name = "input_item");
      super.new(name);
    endfunction

    function void calculate_expected_idx();
      expected_idx = -1;
      for(int i = 0; i < `WIDTH; i++) begin
        if(input_vec[i]) begin
          expected_idx = i;
          break;
        end
      end
      `uvm_info("DBG", $sformatf("input_vec='b%0b, expected_idx=%0d", 
                input_vec, expected_idx), UVM_LOW)
    endfunction

    function void post_randomize();
      calculate_expected_idx();
    endfunction
    
    `uvm_object_utils_begin(input_item)
      `uvm_field_int(input_vec, UVM_ALL_ON)
      `uvm_field_int(expected_idx, UVM_ALL_ON)
    `uvm_object_utils_end
  endclass

  // Transaction: Observed Output
  class output_item extends uvm_sequence_item;
    logic [$clog2(`WIDTH)-1:0] observed_idx;
    
    function new(string name = "output_item");
      super.new(name);
    endfunction
    
    `uvm_object_utils_begin(output_item)
      `uvm_field_int(observed_idx, UVM_ALL_ON)
    `uvm_object_utils_end
  endclass

  // Sequence definition
  class input_sequence extends uvm_sequence #(input_item);
  `uvm_object_utils(input_sequence)

  function new(string name = "input_sequence");
    super.new(name);
  endfunction

  task body();
    logic [`WIDTH-1:0] alt_pat;
    
    // Unified pattern creation flow
    //create_and_send_item('0);                      // All zeros
    
    // Edge cases
    //create_and_send_item({1'b0, {`WIDTH-1{1'b1}}});  // First bit 0
    create_and_send_item({{`WIDTH-1{1'b1}}, 1'b0});  // Last bit 0
    
    // Alternating patterns
    foreach(alt_pat[i]) alt_pat[i] = i[0];         // 0101...
    create_and_send_item(alt_pat);
    create_and_send_item(~alt_pat);                // 1010...
    
    // One-hot patterns
    for(int i=0; i<`WIDTH; i++) begin
      create_and_send_item(1 << i);                // Parameterized shift
    end
    
    // Random patterns using same infrastructure
    repeat(10) begin
      create_and_send_item();                      // No pattern = randomize
    end
  endtask

  // Unified creation task with optional pattern argument
  task create_and_send_item(logic [`WIDTH-1:0] pattern = 'x);
    input_item t = input_item::type_id::create("tr");
    
    if($isunknown(pattern)) begin
      // Random generation path
      if(!t.randomize()) `uvm_error("SEQ", "Randomization failed")
    end
    else begin
      // Directed pattern path
      t.input_vec = pattern;
      t.calculate_expected_idx();
    end
    
    start_item(t);
    finish_item(t);
  endtask
endclass


  // Driver
  class driver extends uvm_driver #(input_item);
    virtual dut_if.DRIVER_MP vif;
    uvm_analysis_port #(input_item) stim_ap;
    
    `uvm_component_utils(driver)
    
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db #(virtual dut_if.DRIVER_MP)::get(this, "", "vif", vif)) begin
        `uvm_fatal("NO_VIF", "Driver: Virtual interface not found!")
      end
    endfunction
    
    function new(string name, uvm_component parent);
      super.new(name, parent);
      stim_ap = new("stim_ap", this);
    endfunction
    
    task run_phase(uvm_phase phase);
      forever begin
        input_item tr;
        seq_item_port.get_next_item(tr);
        vif.driver_cb.input_vec <= tr.input_vec;
        @(vif.driver_cb);
        stim_ap.write(tr);
        seq_item_port.item_done();
      end
    endtask
  endclass

  // Monitor
  class monitor extends uvm_monitor #(output_item);
    virtual dut_if.MONITOR_MP vif;
    uvm_analysis_port #(output_item) out_ap;
    
    `uvm_component_utils(monitor)
    
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      if (!uvm_config_db #(virtual dut_if.MONITOR_MP)::get(this, "", "vif", vif)) begin
        `uvm_fatal("NO_VIF", "Monitor: Virtual interface not found!")
      end
    endfunction
    
    function new(string name, uvm_component parent);
      super.new(name, parent);
      out_ap = new("out_ap", this);
    endfunction
    
    task run_phase(uvm_phase phase);
      forever begin
        output_item tr = output_item::type_id::create("tr");
        @(vif.monitor_cb iff vif.monitor_cb.valid);
        tr.observed_idx = vif.monitor_cb.output_idx;
        out_ap.write(tr);
      end
    endtask
  endclass

  // Scoreboard
  class scoreboard extends uvm_scoreboard;
    uvm_tlm_analysis_fifo #(input_item) stim_fifo;
    uvm_tlm_analysis_fifo #(output_item) out_fifo;
    
    `uvm_component_utils(scoreboard)
    
    function new(string name, uvm_component parent);
      super.new(name, parent);
      stim_fifo = new("stim_fifo", this);
      out_fifo = new("out_fifo", this);
    endfunction
    
    task run_phase(uvm_phase phase);
      input_item stim;
      output_item out;
      forever begin
        stim_fifo.get(stim);
        out_fifo.get(out);
        if(stim.expected_idx !== out.observed_idx) begin
          `uvm_error("SCBD", $sformatf("Mismatch! Exp: %0d, Obs: %0d", stim.expected_idx, out.observed_idx))
        end
      end
    endtask
  endclass

  // Environment
  class env extends uvm_env;
    driver d;
    monitor m;
    scoreboard scbd;
    uvm_sequencer #(input_item) sequencer;
    
    `uvm_component_utils(env)
    
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      sequencer = uvm_sequencer#(input_item)::type_id::create("sequencer", this);
      d = driver::type_id::create("d", this);
      m = monitor::type_id::create("m", this);
      scbd = scoreboard::type_id::create("scbd", this);
    endfunction
    
    function void connect_phase(uvm_phase phase);
      super.connect_phase(phase);
      d.seq_item_port.connect(sequencer.seq_item_export);
      d.stim_ap.connect(scbd.stim_fifo.analysis_export);
      m.out_ap.connect(scbd.out_fifo.analysis_export);
    endfunction
  endclass

  // Test
  class basic_test extends uvm_test;
    env e;
    
    `uvm_component_utils(basic_test)
    
    function new(string name, uvm_component parent);
      super.new(name, parent);
    endfunction
    
    function void build_phase(uvm_phase phase);
      super.build_phase(phase);
      e = env::type_id::create("e", this);
    endfunction
    
    task run_phase(uvm_phase phase);
      phase.raise_objection(this);
      uvm_config_db #(uvm_object_wrapper)::set(
        this, 
        "e.sequencer.main_phase", 
        "default_sequence", 
        input_sequence::type_id::get()
      );
      #5000ns;
      phase.drop_objection(this);
    endtask
  endclass
endpackage

// DUT Interface
interface dut_if #(parameter WIDTH = `WIDTH) (input logic clk, output logic rst_n);
  logic [WIDTH-1:0] input_vec;
  logic [$clog2(WIDTH)-1:0] output_idx;
  logic valid;

  // Clocking blocks
  clocking driver_cb @(posedge clk);
    default output #1step;
    output input_vec;
    input rst_n;
  endclocking

  clocking monitor_cb @(posedge clk);
    default input #1step;
    input output_idx, valid;
  endclocking

  modport DRIVER_MP (clocking driver_cb, input clk);
  modport MONITOR_MP (clocking monitor_cb, input clk);
endinterface

// Top Module
module top;
  `define WIDTH 16  // Set desired width here
  
  import uvm_pkg::*;
  import my_pkg::*;
  
  logic clk;
  logic rst_n;
  dut_if #(`WIDTH) dif(clk, rst_n);
  
  
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end

  initial begin
    dif.rst_n = 0;
    uvm_config_db #(virtual dut_if.DRIVER_MP)::set(null, "uvm_test_top.e.d", "vif", dif);
    uvm_config_db #(virtual dut_if.MONITOR_MP)::set(null, "uvm_test_top.e.m", "vif", dif);
    run_test("basic_test");
    #10 dif.rst_n = 1;
  end
endmodule
