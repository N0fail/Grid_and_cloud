from VM_class import *

def main(queue_tasks, running_tasks, completed_tasks):
    machines = []
    machines.append(VM('solver1', 'solverGroup', '104.41.150.64'))
    machines.append(VM('solver2', 'solverGroup', '104.41.157.159'))
    while True:
        for m in machines:  
            if m.task_info is not None:
                if m.task.isAlive() == False:  # if some task was finished 
                    print("task {} finished".format((m.task_info.n, m.task_info.m)))
                    running_tasks.discard(m.task_info)
                    completed_tasks.add(m.task_info)
                    m.task_info = None
                    
        if len(queue_tasks) > 0:
            task_given = False
            for m in machines:
                if (m.running) and (m.task.isAlive() == False):  # can we give task to already running VM
                    task = queue_tasks.pop(0)
                    m.run_task(task)
                    print("task {} given".format((m.task_info.n, m.task_info.m)))
                    running_tasks.add(task)
                    task_given = True
                    break
            if not task_given:
                for m in machines:  # do we have unused VMs
                    if (m.running == False):
                        task = queue_tasks.pop(0)
                        m.start()
                        print("VM {} started".format(m.name))
                        m.run_task(task)
                        print("task {} given".format((m.task_info.n, m.task_info.m)))
                        running_tasks.add(task)
                        task_given = True
                        break
                if task_given == False: # no VMs available, task stays in queue_tasks
                    time.sleep(1)
        else:  # queue_tasks is empty
            for m in machines:
                if (m.running) and (m.task.isAlive() == False):  # is there running VMs without task
                    print("VM {} stopped".format(m.name))
                    m.stop()
            time.sleep(1)
            