import "./ListTodoLists.css";
import { useRef } from "react";
import { BiSolidTrash } from "react-icons/bi";

/**
 *
 * @param {Object} state - The state to be displayed
 * @param {null|array} state.listSummaries - null, if the data is still being loaded, or an array of list summary objects.
 */
function ListToDoLists({
  listSummaries,
  handleSelectList,
  handleNewToDoList,
  handleDeleteToDoList,
}) {
  const labelRef = useRef();

  if (listSummaries === null) {
    return <div className="ListToDoLists loading">Loading to-do lists ...</div>;
  } else if (listSummaries.length === 0) {
    return <div className="ListToDoLists">There are no to-do lists!</div>;
  }
  return (
    <div className="ListToDoLists">
      <h1>All To-Do Lists</h1>
      <div className="box">
        <label>
          New To-Do List:&nbsp;
          <input id={labelRef} type="text" />
        </label>
        <button
          onClick={() =>
            handleNewToDoList(document.getElementById(labelRef).value)
          }
        >
          New
        </button>
      </div>
      {listSummaries.map((summary) => {
        return (
          <div
            key={summary.id}
            className="summary"
            onClick={() => handleSelectList(summary.id)}
          >
            <span className="name">{summary.name} </span>
            <span className="count">({summary.item_count} items)</span>
            <span className="flex"></span>
            <span
              className="trash"
              onClick={(evt) => {
                evt.stopPropagation();
                handleDeleteToDoList(summary.id);
              }}
            >
              <BiSolidTrash />
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default ListToDoLists;
