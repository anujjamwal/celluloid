module Celluloid
  # Tasks are interruptable/resumable execution contexts used to run methods
  class Task
    attr_reader :type # what type of task is this?

    # Obtain the current task
    def self.current
      task = Thread.current[:task]
      raise "not in task scope" unless task
      task
    end

    # Suspend the running task, deferring to the scheduler
    def self.suspend(value = nil)
      Fiber.yield(value)
    end

    # Run the given block within a task
    def initialize(type)
      @type = type

      actor   = Thread.current[:actor]
      mailbox = Thread.current[:mailbox]

      @fiber = Fiber.new do
        Thread.current[:actor]   = actor
        Thread.current[:mailbox] = mailbox
        Thread.current[:task]    = self

        yield
      end
    end

    # Resume a suspended task, giving it a value to return if needed
    def resume(value = nil)
      waitable = @fiber.resume value

      actor = Thread.current[:actor]
      return waitable unless actor

      actor.add_waiting_task self, waitable if waitable
      nil
    end

    # Is the current task still running?
    def running?; @fiber.alive?; end

    # Nicer string inspect for tasks
    def inspect
      "<Celluloid::Task:0x#{object_id.to_s(16)} @type=#{@type.inspect}, @running=#{@fiber.alive?}>"
    end
  end
end
